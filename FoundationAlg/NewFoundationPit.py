from enum import Enum
from typing import List

class Material(object):
    """The base class of materials"""
    def __init__(self, name, gamma, E) -> None:
        self.name = name
        self.gamma = gamma
        self.E = E
    
    @staticmethod
    def loads(instance: dict):
        name = instance['name']
        gamma = instance['gamma']
        E = instance['E']
        return Material(name, gamma, E)
    
    def to_dict(self):
        return self.__dict__.copy()

class ConcreteMaterial(Material):
    """Class of concrete material, inheriate from materials class

    Args:
        Material (Material): Base class
    """
    def __init__(self, name, gamma, E, v, G = None) -> None:
        self.name = name
        self.gamma = gamma
        self.E = E
        self.v = v
        if G:
            self.G = G
        else:
            self.G = E / (2 * (1 + v))
    
    @staticmethod
    def loads(instance: dict):
        name = instance['name']
        gamma = instance['gamma']
        E = instance['E']
        v = instance['v']
        G = instance['G']
        return ConcreteMaterial(name, gamma, E, v, G)
    
class SupportMaterial(Material):
    """Class of support material, inheriate from materials class"""
    def __init__(self, name, gamma, E, A) -> None:
        super().__init__(name, gamma, E)
        self.name = name
        self.gamma = gamma
        self.E = E
        self.A = A
        self.EA = E * A
    
    @staticmethod
    def loads(instance: dict):
        name = instance['name']
        gamma = instance['gamma']
        E = instance['E']
        A = instance['A']
        return SupportMaterial(name, gamma, E, A)


class EarthType(Enum):
    Rankine = 1
    Coulomb = 2

class SoilMaterial(Material):
    """Class of soil material, inheriate from materials class

    Args:
        Material (Material): Base class
    """
    def __init__(self, name: str, gamma: float,
                 E: float, phi: float, c = 0, sandy=True,
                 varepsilon=0, varphi=0, alpha=0) -> None:
        """Define the soil parameter

        Args:
            name (str): Name of the soil
            gamma (float): Weight of the soil, unit: N/m^-3
            E (int): Elastic Modulus, unit: N/m^2
            phi (float): Internal friction angle, unit: °\degree
            c (int, optional): Cohesive force, unit: Pa. Defaults to 0.
            sandy (bool, optional): Is sandy soil? Defaults to True.
            varepsilon (int, optional): Angle between the back of the retaining wall and the vertical line. Defaults to 0.
            varphi (int, optional): Friction angle of wall and soil. Defaults to 0.
            alpha (int, optional): Angle between soil layer and horizontal plane. Defaults to 0.
        """
        from math import pi, sin
        super().__init__(name, gamma, E)
        self.name = name
        self.gamma = gamma
        self.E = E
        self.phi = phi
        self.c = c
        self.varepsilon = varepsilon
        self.varphi = varphi
        self.alpha = alpha
        from math import tan, atan
        self.phid = (atan(tan(self.phi) + self.c / self.gamma))
        self.K0 = 0
        self.sandy = sandy
        if sandy:
            self.K0 = 1 - sin(phi / 180 * pi)
        else:
            self.K0 = 0.95 - sin(phi / 180 * pi)
        self.Ka = self.get_Ka(phi, EarthType.Coulomb)
        self.Kp = self.get_Kp(phi, EarthType.Coulomb)
        
    def get_Ka(self, phi, type: EarthType):
        from math import sin, cos, tan, pi, sqrt
        phi = phi * pi / 180
        if type == EarthType.Rankine:
            return tan(pi / 4 - phi / 2) ** 2
        if type == EarthType.Coulomb:
            A = sqrt((sin(phi + self.varphi) * sin(phi - self.alpha)) /\
                (cos(self.varepsilon + self.varphi) * cos(self.varepsilon - self.alpha)))
            return cos(phi - self.varepsilon) ** 2 / (cos(self.varepsilon) ** 2 * \
                cos(self.varepsilon + self.varphi) * (1 + A) ** 2)

    def get_Kp(self, phi, type: EarthType):
        from math import sin, cos, tan, pi, sqrt
        phi = phi * pi / 180
        if type == EarthType.Rankine:
            return tan(pi / 4 + phi / 2) ** 2
        if type == EarthType.Coulomb:
            B = sqrt((sin(phi + self.varphi) * sin(phi + self.alpha)) /\
                (cos(self.varepsilon - self.varphi) * cos(self.varepsilon - self.alpha)))
            return cos(phi + self.varepsilon) ** 2 / (cos(self.varepsilon) ** 2 * \
                cos(self.varepsilon - self.varphi) * (1 - B) ** 2)
    
    @staticmethod
    def loads(instance: dict):
        name = instance['name']
        gamma = instance['gamma'] 
        E = instance['E']
        phi = instance['phi'] 
        c = instance['c']
        sandy = instance['sandy']
        varepsilon = instance['varepsilon']
        varphi = instance['varphi']
        alpha = instance['alpha']
        return SoilMaterial(name, gamma, E, phi, c, sandy, varepsilon, varphi, alpha)
    
    def to_dict(self):
        obj = self.__dict__
        obj['phid'] = float(self.phid)
        return obj

class HorizontalSupport(object):
    """Class of the horizontal support of the foundation pit
    """
    def __init__(self, material: SupportMaterial, spaceLength: float) -> None:
        self.Material = material
        self.SpaceLength = spaceLength
        # self.N: Axis force of the support
        self.N = None
    
    def set_material(self, material):
        """Modefy the mateiral of the support

        Args:
            meterial (Material): Target material object
        """
        self.Material = material

    def set_space_length(self, spaceLength):
        """Modify the calculated length
        """
        self.SpaceLength = spaceLength

    @staticmethod
    def loads(instance: dict):
        material = SupportMaterial.loads(instance['Material'])
        space_length = instance['SpaceLength']
        N = instance['N']
        return HorizontalSupport(material, space_length)

    def to_dict(self) -> dict:
        obj = self.__dict__.copy()
        obj['Material'] = self.Material.to_dict()
        return obj       

class BoreHole(object):
    def __init__(self, soils: List[SoilMaterial], intervals:List[dict]) -> None:
        if(len(soils) != len(intervals)):
            raise Exception('The lengths of soils and intervals must be equal!')
        Soils = []
        l = len(soils)
        for i in range(l):
            dic = {
                'soil': soils[i],
                'interval': intervals[i],
            }
            Soils.append(dic)
        Soils = sorted(Soils, key=lambda i: i['interval']['top'])
        self.Soils = Soils

    def get_soil_by_deepth(self, deepth):
        for item in self.Soils:
            if item['interval']['top'] <= deepth and \
                item['interval']['bottom'] >= deepth:
                return item['soil']
        return SoilMaterial('Water', 10, 1E9, 0, 0, True)

    def get_average_soil(self) -> SoilMaterial:
        gamma = E = phi = c = varepsilon = varphi = alpha = intervals = thick = 0
        for item in self.Soils:
            intervals = item['interval']['bottom'] - item['interval']['top']
            gamma += item['soil'].gamma * intervals
            E += item['soil'].E * intervals
            phi += item['soil'].phi * intervals
            c += item['soil'].c * intervals
            varepsilon += item['soil'].varepsilon * intervals
            varphi += item['soil'].varphi * intervals
            alpha += item['soil'].alpha * intervals
            thick += intervals
        
        return SoilMaterial('Average soil', gamma / thick,
                            E / thick, phi / thick, c / thick,
                            True, varepsilon / thick, varphi / thick,
                            alpha / thick)

    @staticmethod
    def loads(instance: list):
        soils = []
        intervals = []
        for item in instance:
            soils.append(SoilMaterial.loads(item['soil']))
            intervals.append(item['interval'])
        return BoreHole(soils, intervals)


    def to_dict(self):
        obj = self.__dict__.copy()
        obj['Soils'] = []
        for i in self.Soils:
            soil = i.copy()
            soil['soil'] = i['soil'].to_dict()
            obj['Soils'].append(soil)
        obj = obj['Soils']
        return obj

class UndergroundDiaphragmWall(object):
    """Class of the underground diaphragm wall of a foundation pit.
    """
    def __init__(self, L, h, material: ConcreteMaterial) -> None:
        """Initial the object of an underground diaphragm wall

        Args:
            L (int): Deepth of the wall, unit: m
            h (float): Thichness of the wall, unit: m
            E (int): Elastic modulus of the wall, unit: Pa
            v (float): Poisson's ratio of the wall: unit: None
            G (int): Shear modulus of the wall, unit: Pa
        """
        self.L = L
        self.h = h
        self.Material = material
        self.I = h ** 3 / 12
        self.E = material.E
        # self.EI: Stiffness of the wall
        self.EI = self.E * self.I
        # self.kar: Shear non-uniformity coefficient of Timoshenko beam
        self.kar = 5 / 6
        self.G = material.G
        self.H = 0
    
    def set_H(self, H: int):
        self.H = H

    def __str__(self) -> str:
        return """The parameters of the underground diaphragm wall are shown below:
            Length: %d m
            Thickness: %f m
            Elastic modulus: %d kPa
            Poisson's ratio: %f
        """ % (self.L, self.h, self.Material.E, self.Material.v)

    @staticmethod
    def loads(instance: dict):
        L = instance['L']
        h = instance['h']
        material = ConcreteMaterial.loads(instance['Material'])
        return UndergroundDiaphragmWall(L, h, material)
     
    def to_dict(self):
        obj = self.__dict__.copy()
        obj['Material'] = self.Material.to_dict()
        return obj

class LRSide(Enum):
    LeftSide = 1
    RightSide = 2

class PressureType(Enum):
    Pa = 1
    Pp = 2

class FoundationPit(object):
    """Class of the foundation pit, contains the parameters for calculating the instance.
    """
    def __init__(self, leftWall: UndergroundDiaphragmWall,
                 rightWall: UndergroundDiaphragmWall,
                 H1, H2, supports: List[HorizontalSupport],
                 supportCount, ds, B, D,
                 boreHole: BoreHole,
                 Palim=0.005, Pplim=0.05,
                 leftOverLoad=0, rightOverLoad=0,
                 leftStrengthLoad=0, rightStrengthLoad=0) -> None:
        
        self.LeftWall = leftWall
        self.RightWall = rightWall
        self.H1 = H1
        self.H2 = H2
        self.ExcaveDeepth = {
            LRSide.LeftSide: H1,
            LRSide.RightSide: H2,
        }
        self.LeftWall.set_H(H1)
        self.RightWall.set_H(H2)

        self.SupportCount = supportCount
        self.Supports = supports

        self.B = B
        self.D = D

        self.BoreHole = boreHole
        self.AverageSoil = boreHole.get_average_soil()
        self.AverageSoil.gamma *= self.D
        
        if ds:
            self.ds = ds
        else:
            self.ds = [3 * i for i in range(supportCount)]
        
        self.update_lim(Palim=Palim, Pplim=Pplim)
        self.LeftOverLoad = leftOverLoad
        self.RightOverLoad = rightOverLoad
        self.LeftStrengthLoad = leftStrengthLoad
        self.RightStrengthLoad = rightStrengthLoad

    def get_overload(self, side: LRSide):
        overload = 0
        if side == LRSide.LeftSide:
            overload = self.LeftOverLoad
        if side == LRSide.RightSide:   
            overload = self.RightOverLoad
        return overload * self.D
    
    def get_strength_load(self, side: LRSide):
        overload = 0
        if side == LRSide.LeftSide:
            overload = self.LeftStrengthLoad
        if side == LRSide.RightSide:
            overload = self.RightStrengthLoad
        return overload * self.D

    def cal_top_pressure(self, side: LRSide, type: PressureType, layer: int, H=0):
        sigma_x = 0
        if type == PressureType.Pa:
            # 默认主动土压力计算深度从地面开始
            for i in range(layer):
                soilLayer = self.BoreHole.Soils[i]
                gamma = soilLayer['soil'].gamma
                height = soilLayer['interval']['bottom'] - soilLayer['interval']['top']
                sigma_x += gamma * height
            sigma_x += self.get_overload(side)

        if type == PressureType.Pp:
            sb = H
            index = self.get_soil_layer(H)
            for i in range(index, layer):
                soilLayer = self.BoreHole.Soils[i]
                gamma = soilLayer['soil'].gamma
                height = soilLayer['interval']['bottom'] - sb
                sb = soilLayer['interval']['bottom']
                sigma_x += gamma * height
            sigma_x += self.get_strength_load(side)

        return sigma_x

    def get_soil_layer(self, depth):
        index = 0
        for i in self.BoreHole.Soils:
            if i['interval']['top'] <= depth <= i['interval']['bottom']:
                return index
            index += 1
        return -1

    def P0(self, z, side: LRSide, type: PressureType):
        return self.AverageSoil.K0 * (self.AverageSoil.gamma * z + self.analyse_overload(side, type))

    def Pacr(self, z, side: LRSide, pType: PressureType, type=EarthType.Rankine):
        soil = self.AverageSoil
        overload = self.analyse_overload(side, pType)
        if type == EarthType.Rankine:
            from sympy import sqrt
            Ka = soil.Ka
            return Ka * (self.AverageSoil.gamma * z + overload) -\
                2 * self.AverageSoil.c * sqrt(Ka)
        if type == EarthType.Coulomb:
            from sympy import tan, atan, pi
            phi = soil.phi / 180 * pi
            H = self.ExcaveDeepth[side]
            phi = atan(tan(phi) + soil.c / soil.gamma / H)
            self.AverageSoil.phid = phi
            phi = phi * 180 / pi
            Ka = soil.get_Ka(phi, type)
            return Ka * (self.AverageSoil.gamma * z + overload)
        return 0

    def analyse_overload(self, side: LRSide, type: PressureType):
        if type == PressureType.Pa:
            return self.get_overload(side)
        if type == PressureType.Pp:
            return self.get_strength_load(side)

    def Ppcr(self, z, side: LRSide, pType: PressureType, type=EarthType.Rankine):
        soil = self.AverageSoil
        overload = self.analyse_overload(side, pType)
        if type == EarthType.Rankine:
            from sympy import sqrt
            Kp = soil.Kp
            return Kp * (self.AverageSoil.gamma * z + overload) +\
                2 * self.AverageSoil.c * sqrt(Kp)
        if type == EarthType.Coulomb:
            from sympy import tan, atan, pi
            phi = soil.phi / 180 * pi
            H = self.ExcaveDeepth[side]
            phi = atan(tan(phi) + soil.c / soil.gamma / H)
            self.AverageSoil.phid = phi
            phi = phi * 180 / pi
            Kp = soil.get_Kp(phi, type)
            return Kp * (self.AverageSoil.gamma * z + overload)
        return 0

    def Pa(self, z, w, side: LRSide, alpha=0.9):
        P0 = self.P0(z, side)
        Pacr = self.Pacr(z, side)
        sa = 0
        if side ==LRSide.LeftSide:
            sa = self.PalimWl
        if side == LRSide.RightSide:
            sa = self.PalimWr
        from sympy import exp
        return P0 - (P0 - Pacr) * (w / sa) * exp(alpha * (1 - w / sa))

    def Pp(self, z, w, side: LRSide, alpha=0.9):
        H = 0
        if side == LRSide.LeftSide:
            H = self.H1
        if side == LRSide.RightSide:
            H = self.H2
        
        P0 = self.P0(z - H, side)
        Ppcr = self.Ppcr(z - H, side)
        sp = 0
        if side ==LRSide.LeftSide:
            sp = self.PplimWl
        if side == LRSide.RightSide:
            sp = self.PplimWr
        from sympy import exp
        return P0 + (Ppcr - P0) * (w / sp) * exp(alpha * (1 - w / sp))

    def update_lim(self, Palim=0.005, Pplim=0.05):
        self.Palim = Palim
        self.Pplim = Pplim
        self.PalimWl = self.LeftWall.L * Palim
        self.PplimWl = self.LeftWall.L * Pplim
        self.PalimWr = self.RightWall.L * Palim
        self.PplimWr = self.RightWall.L * Pplim
    
    def __str__(self) -> str:
        return """
        The foundation pit is excavated %dm on the left and %dm on the right,
        The length of left support is %dm, and the right is %dm,
        There are %d supports in it.
        """ % (self.H1, self.H2, self.LeftWall.L, self.RightWall.L, self.SupportCount)
    
    @staticmethod
    def loads(instance: dict):
        leftWall = UndergroundDiaphragmWall.loads(instance['LeftWall'])
        rightWall = UndergroundDiaphragmWall.loads(instance['RightWall'])
        H1 = instance['H1']
        H2 = instance['H2']
        supports = [HorizontalSupport.loads(i) for i in instance['Supports']]
        support_count = instance['SupportCount']
        ds = instance['ds']
        B = instance['B']
        D = instance['D']
        borehole = BoreHole.loads(instance['BoreHole'])
        Palim = instance['Palim']
        Pplim = instance['Pplim']
        left_overload = instance['LeftOverLoad']
        right_overload = instance['RightOverLoad']
        left_strength_load = instance['LeftStrengthLoad']
        right_strength_load = instance['RightStrengthLoad']
        return FoundationPit(leftWall, rightWall, H1, H2, supports,
                                support_count, ds, B, D, borehole, 
                                leftOverLoad=left_overload, rightOverLoad=right_overload,
                                leftStrengthLoad=left_strength_load, 
                                rightStrengthLoad=right_strength_load)

    def to_dict(self):
        obj = self.__dict__.copy()
        obj['LeftWall'] = self.LeftWall.to_dict()
        obj['RightWall'] = self.RightWall.to_dict()
        obj['Supports'] = [i.to_dict() for i in self.Supports]
        obj['BoreHole'] = self.BoreHole.to_dict()
        obj['AverageSoil'] = self.AverageSoil.to_dict()
        obj['ExcaveDeepth'] = {
            "LeftSide": self.ExcaveDeepth[LRSide.LeftSide],
            "RightSide": self.ExcaveDeepth[LRSide.RightSide]
        }
        return obj