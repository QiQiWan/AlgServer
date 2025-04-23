from sympy import *
from .NewFoundationPit import *
import numpy as np

class BoundaryCondition(Enum):
    TopHinge = 1
    BottomHinge = 2
    BottomFixed = 3

class BoundaryType(Enum):
    Hinge = 1
    Fixed = 2

class BeamModel(Enum):
    EulerBernoulliBeam = 1
    TimoshenkoBeam = 2

class EnergyMethodSolver(object):
    def __init__(self, z, foundationPit: FoundationPit, hm=8) -> None:
        self.z = z
        self.s = symbols('s')
        self.Ns = [symbols(f'N_{i + 1}') for i in range(foundationPit.support_count)]
        self.NEA = [i.Material.EA for i in foundationPit.supports]
        self.foundation_pit = foundationPit
        # define the earth pressure function         
        self.Pal = self.get_pressure_function(LRSide.LeftSide, PressureType.Pa)
        self.Par = self.get_pressure_function(LRSide.RightSide, PressureType.Pa)
        self.Ppl = self.get_pressure_function(LRSide.LeftSide, PressureType.Pp)
        self.Ppr = self.get_pressure_function(LRSide.RightSide, PressureType.Pp)
        self.bore_hole = foundationPit.bore_hole
        self.hm = hm

    @staticmethod
    def init_symbol():
        return symbols('z')

    def cal_middle_point(self, side: LRSide, type: PressureType):
        """Cal the middle point for the support pile

        Args:
            side (LRSide): Define the side of the foudation pit
            type (PressureType): Define the type of the earth pressure

        Returns:
            [float]: Position of the middle point 
        """
        L = H = 0
        if side == LRSide.LeftSide:
            L = self.foundation_pit.left_wall.L
            if type == PressureType.Pp:
                H = self.foundation_pit.H1
        else:
            L = self.foundation_pit.right_wall.L
            if type == PressureType.Pp:
                H = self.foundation_pit.H2
        return (L - H) / 2

    def get_pressure_function(self, side: LRSide, type: PressureType, alpha=0.9):
        """Cal the earth pressure function for active and passive pressure
        Args:
            side (LRSide): the side of foudation pit
            type (PressureType): the type of earth pressure
            alpha (float, optional): calculation coefficient. Defaults to 0.9.

        Returns:
            [expr]: specific earth pressure function
        """
        paLim = ppLim = 0
        pacr = ppcr = p0 = 0
        ML = self.cal_middle_point(side, type)
        if side == LRSide.LeftSide:
            paLim = self.foundation_pit.Pa_lim_wl
            ppLim = self.foundation_pit.Pp_lim_wl
        if side == LRSide.RightSide:
            paLim = self.foundation_pit.Pa_lim_wr
            ppLim = self.foundation_pit.Pp_lim_wr

        pacr = self.foundation_pit.Pacr(self.z, side, type, EarthType.Coulomb)
        pacr = pacr.subs(self.z, ML)
        ppcr = self.foundation_pit.Ppcr(self.z, side, type, EarthType.Coulomb)
        ppcr = ppcr.subs(self.z, ML)
        p0 = self.foundation_pit.P0(self.z, side, type).subs(self.z, ML)
        return self.exponential_model(p0, pacr, ppcr, paLim, ppLim, 2 * ML, alpha=alpha)

    # Chen YeKai exponential model of earth pressure
    def exponential_model(self, p0, pacr, ppcr, paLim, ppLim, L, alpha=0.9, order=5):
        """AI is creating summary for ExponentialModel

        Args:
            p0 ([type]): [description]
            pacr ([type]): [description]
            ppcr ([type]): [description]
            paLim ([type]): [description]
            ppLim ([type]): [description]
            L ([type]): [description]
            alpha (float, optional): [description]. Defaults to 0.9.
            order (int, optional): [description]. Defaults to 5.

        Returns:
            [type]: [description]
        """
        Pa = p0 - (p0 - pacr) * self.s / paLim * exp(alpha * (1 - self.s / paLim))
        # Pa = Pa / self.z
        Pp = p0 + (ppcr - p0) * self.s / ppLim * exp(alpha * (1 - self.s / ppLim))
        # Pp = Pp / self.z
        
        X1 = [i / 1000 for i in range(int(paLim * 1E3) + 50)]
        X2 = [-i / 1000 for i in range(1, int(ppLim * 1E3) + 50)]
        X = X2[::-1] + X1
        X = np.array(X, dtype=float)

        Y1 = [Pa.subs(self.s, abs(i)) for i in X1]
        Y2 = [Pp.subs(self.s, abs(i)) for i in X2]
        Y = Y2[::-1] + Y1
        Y = np.array(Y, dtype=float)
        zi = np.polyfit(X, Y, order)

        func = 0
        origin = order
        while order >= 0:
            func += zi[origin - order] * self.s ** order
            order -= 1
        # 由于土压力随深度呈线性关系，由于选用的中点计算，因此在积分时需要对深度进行归一化
        return func * self.z / L

    # Splice deformation function
    def polynomial_function(self, sym):
        w = 0
        coeffs = []
        index = 1
        for i in range(self.hm):
            coeff = symbols(f'{sym}_{index}')
            w += coeff * self.z ** i
            index += 1 
            coeffs.append(coeff)
        return w, coeffs
    
    def null_space_equations(self, ws: list, ls: list, boundary: BoundaryCondition):
        eqs = []
        if boundary == BoundaryCondition.TopHinge:
            for w in ws:
                eqs.append(Eq(w.subs(self.z, 0), 0))

        l = len(ws)
        if boundary == BoundaryCondition.BottomHinge:
            for i in range(l):
                eqs.append(Eq(ws[i].subs(self.z, ls[i]), 0))
        
        if boundary == BoundaryCondition.BottomFixed:
            for i in range(l):
                eqs.append(Eq(ws[i].subs(self.z, ls[i]), 0))
                eqs.append(Eq(ws[i].diff(self.z).subs(self.z, ls[i]), 0))
        return eqs
                
    def boundary_eqs(self, w, l, type: BoundaryType):
        eqs = []
        eqs.append(Eq(w.subs(self.z, l), 0))
        if type == BoundaryType.Fixed:
            eqs.append(Eq(w.diff(self.z).subs(self.z, l), 0))
        return eqs

    def deformation_coordination_eqs(self, wl, wr):
        eqs = []
        supportCount = self.foundation_pit.support_count
        ds = self.foundation_pit.ds
        for i in range(supportCount):
            eqs.append(Eq(wl.subs(self.z, ds[i]) + wr.subs(self.z, ds[i]), self.Ns[i] *\
                self.foundation_pit.B / self.NEA[i]))
        return eqs

    def external_force_work(self, wl, wr, dsal, dsar):
        Wl = 0 
        Wr = 0
        # 主动土压力区域外力做功
        # Pacrl = self.FoundationPit.Pacr(self.z, LRSide.LeftSide, PressureType.Pa, EarthType.Coulomb)
        # P0l = self.FoundationPit.P0(self.z, LRSide.LeftSide, PressureType.Pa)
        # Pacrr = self.FoundationPit.Pacr(self.z, LRSide.RightSide, PressureType.Pa, EarthType.Coulomb)
        # P0r = self.FoundationPit.P0(self.z, LRSide.RightSide, PressureType.Pa)
        # PaLimWl = self.FoundationPit.PalimWl
        # PaLimWr = self.FoundationPit.PalimWr
        # Wl += integrate((2 * P0l + (Pacrl - P0l) * 1.9 * wl / PaLimWl) * wl/ 2, (self.z, 0, dsal[-1]))
        # Wr += integrate((2 * P0r + (Pacrr - P0r) * 1.9 * wr / PaLimWr) * wr/ 2, (self.z, 0, dsar[-1]))

        Wl += self.active_earth_work(dsal[-1], wl, LRSide.LeftSide)
        Wr += self.active_earth_work(dsar[-1], wr, LRSide.RightSide)

        # 被动区外力做功
        # Ppcrl = self.FoundationPit.Pacr(self.z - dsal[-2], LRSide.LeftSide, PressureType.Pp, EarthType.Coulomb)
        # P0l = self.FoundationPit.P0(self.z - dsal[-2], LRSide.LeftSide, PressureType.Pp)
        # Ppcrr = self.FoundationPit.Pacr(self.z - dsar[-2], LRSide.RightSide, PressureType.Pp, EarthType.Coulomb)
        # P0r = self.FoundationPit.P0(self.z - dsar[-2], LRSide.RightSide, PressureType.Pp)
        # PpLimWl = self.FoundationPit.PplimWl
        # PpLimWr = self.FoundationPit.PplimWr
        # print(dsal[-2])
        # Wl -= integrate((2 * P0l + (Ppcrl - P0l) * 1.9 * wl / PpLimWl) * wl / 2, (self.z, dsal[-2], dsal[-1]))
        # Wr -= integrate((2 * P0r + (Ppcrr - P0r) * 1.9 * wr / PpLimWr) * wr / 2, (self.z, dsar[-2], dsar[-1]))

        Wl -= self.passive_earth_work(dsal[-2], dsal[-1], wl, LRSide.LeftSide)
        Wr -= self.passive_earth_work(dsar[-2], dsar[-1], wr, LRSide.RightSide)
        return Wl, Wr
    
    def active_earth_work(self, L, w, side):
        W = 0
        PaLim = self.foundation_pit.Pa_lim_wl
        if side == LRSide.RightSide:
            PaLim = self.foundation_pit.Pa_lim_wr
        s_bottom = 0 # 表示土层底端
        soil_layer_index = 0 # 表示开始积分指定地层
        while s_bottom < L:
            soi_layer = self.bore_hole.soils[soil_layer_index]
            topPressure = self.foundation_pit.cal_top_pressure(side, PressureType.Pa, soil_layer_index)
            topDepth = self.bore_hole.soils[soil_layer_index]['interval']['top']
            P0 = (topPressure + soi_layer['soil'].gamma * (self.z - topDepth)) * soi_layer['soil'].K0
            Pacr = (topPressure + soi_layer['soil'].gamma * (self.z - topDepth)) * soi_layer['soil'].Ka
            # 解决当定义的土层深度大于支护桩长的问题
            if soi_layer['interval']['bottom'] > L:
                s_bottom = L
            else:
                s_bottom = soi_layer['interval']['bottom']
            W += integrate((2 * P0 + (Pacr - P0) * 1.9 * w / PaLim) * w / 2, (self.z, soi_layer['interval']['top'], s_bottom))
            soil_layer_index += 1
        
        return W

    def passive_earth_work(self, H, L, w, side):
        W = 0
        Pp_lim = self.foundation_pit.Pp_lim_wl
        if side == LRSide.RightSide:
            Pp_lim = self.foundation_pit.Pp_lim_wr
        s_bottom = H
        soil_layer_index = self.foundation_pit.get_soil_layer(s_bottom)
        while s_bottom < L:
            soil_layer = self.bore_hole.soils[soil_layer_index]
            top_pressure = self.foundation_pit.cal_top_pressure(side, PressureType.Pp, soil_layer_index, H)
            P0 = (top_pressure + soil_layer['soil'].gamma * self.z) * soil_layer['soil'].K0
            Ppcr = (top_pressure + soil_layer['soil'].gamma * self.z) * soil_layer['soil'].Ka
            if soil_layer['interval']['bottom'] > L:
                W += integrate((2 * P0 + (Ppcr - P0) * 1.9 * w / Pp_lim) * w / 2, (self.z, s_bottom, L))
            else:
                W += integrate((2 * P0 + (Ppcr - P0) * 1.9 * w / Pp_lim) * w / 2, (self.z, s_bottom, soil_layer['interval']['bottom']))
            s_bottom = soil_layer['interval']['bottom']
            soil_layer_index += 1
        
        return W
    
    def strain_energy(self, wl, wr, beamModel=BeamModel.EulerBernoulliBeam):
        Ul = 0 # 左侧支护桩的应变能
        Ur = 0 # 右侧支护桩的应变能
        L1 = self.foundation_pit.left_wall.L
        L2 = self.foundation_pit.right_wall.L
        EI = self.foundation_pit.left_wall.EI
        EIl = self.foundation_pit.left_wall.EI
        EIr = self.foundation_pit.right_wall.EI
        Ul += integrate(EI * wl.diff(self.z, 2) ** 2 / 2, (self.z, 0, L1))
        Ur += integrate(EI * wr.diff(self.z, 2) ** 2 / 2, (self.z, 0, L2))

        if beamModel == BeamModel.TimoshenkoBeam:
            alpha = 6 / 5
            GAl = self.foundation_pit.left_wall.G * self.foundation_pit.left_wall.h * self.foundation_pit.D
            GAr = self.foundation_pit.right_wall.G * self.foundation_pit.left_wall.h * self.foundation_pit.D
            Ul += alpha * EI ** 2 / 2 / GAl * integrate(wl.diff(self.z, 3) ** 2, (self.z, 0, L1))
            Ur += alpha * EI ** 2 / 2 / GAr * integrate(wr.diff(self.z, 3) ** 2, (self.z, 0, L2))
        
        return Ul, Ur

    def solve(self):
        L1 = self.foundation_pit.left_wall.L
        L2 = self.foundation_pit.right_wall.L
        H1 = self.foundation_pit.H1
        H2 = self.foundation_pit.H2
        ds = self.foundation_pit.ds
        dsal = [0] + ds + [H1] + [L1]
        dsar = [0] + ds + [H2] + [L2]
        support_count = self.foundation_pit.support_count

        # print(dsal)
        # print(dsar)
        Ns = self.Ns
        NEA = self.NEA
        # 计算坑中坑土压力参数
        wl, c_set =  self.polynomial_function('B')# wl多项式参数列表
        wr, b_set = self.polynomial_function('C')

        # 边界条件与变形协调条件
        eqs = self.null_space_equations([wl, wr], [L1, L2], BoundaryCondition.BottomFixed)
        eqs = eqs + self.deformation_coordination_eqs(wl, wr)
        result = solve(eqs, b_set + c_set)
        wl = wl.subs(result)
        wr = wr.subs(result)
        # wm = wm.subs(result)
        for key in result:
            if key in b_set:
                b_set.remove(key)
            if key in c_set:
                c_set.remove(key)
            # if key in DSet:
            #     DSet.remove(key)

        # 支护桩外力做功
        Wl, Wr = self.external_force_work(wl, wr, dsal, dsar)

        # 支护桩变形能
        Ul, Ur = self.strain_energy(wl, wr)

        # 支撑轴力应变能
        Ne = 0
        for i in range(support_count):
            Ne += Ns[i] ** 2 * self.foundation_pit.B / 2 / NEA[i]
        TotU = Ul + Ur - Wl - Wr + Ne
        eqs = []
        # 最小势能原理，计算总势能变分
        for i in b_set:
            eqs.append(Eq(TotU.diff(i), 0))
        for i in c_set:
            eqs.append(Eq(TotU.diff(i), 0))
        for i in Ns:
            eqs.append(Eq(TotU.diff(i), 0))
        result = solve(eqs, b_set + c_set + Ns)
        wl = wl.subs(result)
        wr = wr.subs(result)
        return result, wl, wr

