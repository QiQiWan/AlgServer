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
        self.Ns = [symbols(f'N_{i + 1}') for i in range(foundationPit.SupportCount)]
        self.NEA = [i.Material.EA for i in foundationPit.Supports]
        self.FoundationPit = foundationPit
        # define the earth pressure function         
        self.Pal = self.GetPressureFunction(LRSide.LeftSide, PressureType.Pa)
        self.Par = self.GetPressureFunction(LRSide.RightSide, PressureType.Pa)
        self.Ppl = self.GetPressureFunction(LRSide.LeftSide, PressureType.Pp)
        self.Ppr = self.GetPressureFunction(LRSide.RightSide, PressureType.Pp)
        self.BoreHole = foundationPit.BoreHole
        self.hm = hm

    @staticmethod
    def init_symbol():
        return symbols('z')

    def CalMiddlePoint(self, side: LRSide, type: PressureType):
        """Cal the middle point for the support pile

        Args:
            side (LRSide): Define the side of the foudation pit
            type (PressureType): Define the type of the earth pressure

        Returns:
            [float]: Position of the middle point 
        """
        L = H = 0
        if side == LRSide.LeftSide:
            L = self.FoundationPit.LeftWall.L
            if type == PressureType.Pp:
                H = self.FoundationPit.H1
        else:
            L = self.FoundationPit.RightWall.L
            if type == PressureType.Pp:
                H = self.FoundationPit.H2
        return (L - H) / 2

    def GetPressureFunction(self, side: LRSide, type: PressureType, alpha=0.9):
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
        ML = self.CalMiddlePoint(side, type)
        if side == LRSide.LeftSide:
            paLim = self.FoundationPit.PalimWl
            ppLim = self.FoundationPit.PplimWl
        if side == LRSide.RightSide:
            paLim = self.FoundationPit.PalimWr
            ppLim = self.FoundationPit.PplimWr

        pacr = self.FoundationPit.Pacr(self.z, side, type, EarthType.Coulomb)
        pacr = pacr.subs(self.z, ML)
        ppcr = self.FoundationPit.Ppcr(self.z, side, type, EarthType.Coulomb)
        ppcr = ppcr.subs(self.z, ML)
        p0 = self.FoundationPit.P0(self.z, side, type).subs(self.z, ML)
        return self.ExponentialModel(p0, pacr, ppcr, paLim, ppLim, 2 * ML, alpha=alpha)

    # Chen YeKai exponential model of earth pressure
    def ExponentialModel(self, p0, pacr, ppcr, paLim, ppLim, L, alpha=0.9, order=5):
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
    def PolynomialFunction(self, sym):
        w = 0
        coeffs = []
        index = 1
        for i in range(self.hm):
            coeff = symbols(f'{sym}_{index}')
            w += coeff * self.z ** i
            index += 1 
            coeffs.append(coeff)
        return w, coeffs
    
    def NullSpaceEquations(self, ws: list, ls: list, boundary: BoundaryCondition):
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
                
    def BoundaryEqs(self, w, l, type: BoundaryType):
        eqs = []
        eqs.append(Eq(w.subs(self.z, l), 0))
        if type == BoundaryType.Fixed:
            eqs.append(Eq(w.diff(self.z).subs(self.z, l), 0))
        return eqs

    def DeformationCoordinationEqs(self, wl, wr):
        eqs = []
        supportCount = self.FoundationPit.SupportCount
        ds = self.FoundationPit.ds
        for i in range(supportCount):
            eqs.append(Eq(wl.subs(self.z, ds[i]) + wr.subs(self.z, ds[i]), self.Ns[i] *\
                self.FoundationPit.B / self.NEA[i]))
        return eqs

    def ExternalForceWork(self, wl, wr, dsal, dsar):
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

        Wl += self.ActiveEarthWork(dsal[-1], wl, LRSide.LeftSide)
        Wr += self.ActiveEarthWork(dsar[-1], wr, LRSide.RightSide)

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

        Wl -= self.PassiveEarthWork(dsal[-2], dsal[-1], wl, LRSide.LeftSide)
        Wr -= self.PassiveEarthWork(dsar[-2], dsar[-1], wr, LRSide.RightSide)
        return Wl, Wr
    
    def ActiveEarthWork(self, L, w, side):
        W = 0
        PaLim = self.FoundationPit.PalimWl
        if side == LRSide.RightSide:
            PaLim = self.FoundationPit.PalimWr
        SBottom = 0 # 表示土层底端
        soilLayerIndex = 0 # 表示开始积分指定地层
        while SBottom < L:
            soilLayer = self.BoreHole.Soils[soilLayerIndex]
            topPressure = self.FoundationPit.cal_top_pressure(side, PressureType.Pa, soilLayerIndex)
            topDepth = self.BoreHole.Soils[soilLayerIndex]['interval']['top']
            P0 = (topPressure + soilLayer['soil'].gamma * (self.z - topDepth)) * soilLayer['soil'].K0
            Pacr = (topPressure + soilLayer['soil'].gamma * (self.z - topDepth)) * soilLayer['soil'].Ka
            # 解决当定义的土层深度大于支护桩长的问题
            if soilLayer['interval']['bottom'] > L:
                SBottom = L
            else:
                SBottom = soilLayer['interval']['bottom']
            W += integrate((2 * P0 + (Pacr - P0) * 1.9 * w / PaLim) * w / 2, (self.z, soilLayer['interval']['top'], SBottom))
            soilLayerIndex += 1
        
        return W

    def PassiveEarthWork(self, H, L, w, side):
        W = 0
        PpLim = self.FoundationPit.PplimWl
        if side == LRSide.RightSide:
            PpLim = self.FoundationPit.PplimWr
        SBottom = H
        soilLayerIndex = self.FoundationPit.get_soil_layer(SBottom)
        while SBottom < L:
            soilLayer = self.BoreHole.Soils[soilLayerIndex]
            topPressure = self.FoundationPit.cal_top_pressure(side, PressureType.Pp, soilLayerIndex, H)
            P0 = (topPressure + soilLayer['soil'].gamma * self.z) * soilLayer['soil'].K0
            Ppcr = (topPressure + soilLayer['soil'].gamma * self.z) * soilLayer['soil'].Ka
            if soilLayer['interval']['bottom'] > L:
                W += integrate((2 * P0 + (Ppcr - P0) * 1.9 * w / PpLim) * w / 2, (self.z, SBottom, L))
            else:
                W += integrate((2 * P0 + (Ppcr - P0) * 1.9 * w / PpLim) * w / 2, (self.z, SBottom, soilLayer['interval']['bottom']))
            SBottom = soilLayer['interval']['bottom']
            soilLayerIndex += 1
        
        return W
    
    def StrainEnergy(self, wl, wr, beamModel=BeamModel.EulerBernoulliBeam):
        Ul = 0 # 左侧支护桩的应变能
        Ur = 0 # 右侧支护桩的应变能
        L1 = self.FoundationPit.LeftWall.L
        L2 = self.FoundationPit.RightWall.L
        EI = self.FoundationPit.LeftWall.EI
        EIl = self.FoundationPit.LeftWall.EI
        EIr = self.FoundationPit.RightWall.EI
        Ul += integrate(EI * wl.diff(self.z, 2) ** 2 / 2, (self.z, 0, L1))
        Ur += integrate(EI * wr.diff(self.z, 2) ** 2 / 2, (self.z, 0, L2))

        if beamModel == BeamModel.TimoshenkoBeam:
            alpha = 6 / 5
            GAl = self.FoundationPit.LeftWall.G * self.FoundationPit.LeftWall.h * self.FoundationPit.D
            GAr = self.FoundationPit.RightWall.G * self.FoundationPit.LeftWall.h * self.FoundationPit.D
            Ul += alpha * EI ** 2 / 2 / GAl * integrate(wl.diff(self.z, 3) ** 2, (self.z, 0, L1))
            Ur += alpha * EI ** 2 / 2 / GAr * integrate(wr.diff(self.z, 3) ** 2, (self.z, 0, L2))
        
        return Ul, Ur

    def Solve(self):
        L1 = self.FoundationPit.LeftWall.L
        L2 = self.FoundationPit.RightWall.L
        H1 = self.FoundationPit.H1
        H2 = self.FoundationPit.H2
        ds = self.FoundationPit.ds
        dsal = [0] + ds + [H1] + [L1]
        dsar = [0] + ds + [H2] + [L2]
        supportCount = self.FoundationPit.SupportCount

        # print(dsal)
        # print(dsar)
        Ns = self.Ns
        NEA = self.NEA
        # 计算坑中坑土压力参数
        wl, CSet =  self.PolynomialFunction('B')# wl多项式参数列表
        wr, BSet = self.PolynomialFunction('C')

        # 边界条件与变形协调条件
        eqs = self.NullSpaceEquations([wl, wr], [L1, L2], BoundaryCondition.BottomFixed)
        eqs = eqs + self.DeformationCoordinationEqs(wl, wr)
        result = solve(eqs, BSet + CSet)
        wl = wl.subs(result)
        wr = wr.subs(result)
        # wm = wm.subs(result)
        for key in result:
            if key in BSet:
                BSet.remove(key)
            if key in CSet:
                CSet.remove(key)
            # if key in DSet:
            #     DSet.remove(key)

        # 支护桩外力做功
        Wl, Wr = self.ExternalForceWork(wl, wr, dsal, dsar)

        # 支护桩变形能
        Ul, Ur = self.StrainEnergy(wl, wr)

        # 支撑轴力应变能
        Ne = 0
        for i in range(supportCount):
            Ne += Ns[i] ** 2 * self.FoundationPit.B / 2 / NEA[i]
        TotU = Ul + Ur - Wl - Wr + Ne
        eqs = []
        # 最小势能原理，计算总势能变分
        for i in BSet:
            eqs.append(Eq(TotU.diff(i), 0))
        for i in CSet:
            eqs.append(Eq(TotU.diff(i), 0))
        for i in Ns:
            eqs.append(Eq(TotU.diff(i), 0))
        result = solve(eqs, BSet + CSet + Ns)
        wl = wl.subs(result)
        wr = wr.subs(result)
        return result, wl, wr

