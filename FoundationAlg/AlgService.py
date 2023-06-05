from .NewFoundationPit import *
from .UpdateEnergy import EnergyMethodSolver
import json
import time

# Create your models here.
class FoundationPitAnalysor(object):

    def __init__(self, queries):
        """生成一个基坑计算参数模型，调度计算任务，生成任务ID

        Args:
            queries (str): 基坑计算参数列表，是一个json文件
        """
        paramsDict = json.loads(queries)
        try:
            self.CheckParams(paramsDict)
        except Exception as err:
            print(err)
            return err, False
        self.foundation_pit = self.CreateFoundation(paramsDict)
        return self, True


    def CheckParams(self, queries: dict):
        # 检查构造一个基坑对象所需要的所有参数
        paraList = ['E', 'h', 'D', 'v', 'L1', 'L2', 'H1', 'H2', 'B', 'Supports', 'ds',\
                    'LeftWall', 'RightWall', 'BoreHole', 'leftOverLoad', 'rightOverLoad',\
                    'leftStrengthLoad', 'rightStrengthLoad']
        for item in paraList:
            if item not in queries:
                raise Exception(f'The argument {item} is not found!')

        # 对某些复杂参数进行进一步检查
        supportList = ['Count', 'SupportMaterial', 'Names']
        for item in supportList:
            if item not in queries['Supports']:
                raise Exception(f'The arguement {item} in support is not found!')

        # 对两侧的支护桩参数进行检查
        pileList = ['Name', 'Meterial']
        for item in pileList:
            if item not in queries['LeftWall']:
                raise Exception(f'The argument {item} in LeftWall is not found!')
            if item not in queries['RightWall']:
                raise Exception(f'The argument {item} in RightWall is not found!')

        # 对土层钻孔数据进行检查
        soilList = ['Name', 'gamma', 'E', 'phi', 'c', 'interval']
        for item in soilList:
            for soillayer in queries['BoreHole']:
                if item not in soillayer:
                    name = soillayer['Name']
                    raise Exception(f'The argument {item} in soillayer {name} is not Found!')
        return True

    def CreateFoundation(self, queries: dict):
        # 定义支护桩
        leftWall = queries['LeftWall']
        material = leftWall['Meterial']
        concreteMaterial = ConcreteMaterial(material['Name'], material['gamma'], \
                                            material['E'], material['A'])
        leftWall = UndergroundDiaphragmWall(queries['L1'], queries['h'], concreteMaterial)

        rightWall = queries['RightWall']
        material = rightWall['Material']
        concreteMaterial = ConcreteMaterial(material['Name'], material['gamma'], \
                                            material['E'], material['A'])
        rightWall = UndergroundDiaphragmWall(queries['L2'], queries['h'], concreteMaterial)
        # Declear the horizontal supports
        supports = queries['Supports']
        supportCount = supports['Count']
        materials = supports['Materials']
        braceMaterials = []
        braceMaterials.append(braceMaterials.append(SupportMaterial(item['Name'],
                                                                    item['gamma'], 
                                                                    item['E'],
                                                                    item['A'])) for item in materials)
        
        # 定义土层参数
        soillayouts = queries['BoreHole']
        soils = [SoilMaterial(i['Name'], i['gamma'], i['E'], i['phi'], i['c']) for i in soillayouts]
        intervals = [i['interval'] for i in soillayouts]
        borehole = BoreHole(soils, intervals)
        
        supports = [HorizontalSupport(material, queries['B']) for material in braceMaterials]
        foundationPit = FoundationPit(leftWall, rightWall, queries['H1'], queries['H2'], supports,
                                      supportCount, queries['ds'], queries['B'], queries['D'], borehole,\
                                      leftOverLoad=queries['leftOverLoad'], rightOverLoad=queries['rightOverLoad'],\
                                      leftStrengthLoad=queries['leftStrengthLoad'], rightStrengthLoad=queries['rightStrengthLoad'])
        return foundationPit

    def calculate(self, id):
        self.ID = id
        z = EnergyMethodSolver.init_symbol()
        solver = EnergyMethodSolver(z, self.foundation_pit, 10)
        _, wl, wr = solver.Solve()
        obj = {
            'ID': id,
            'L1': self.foundation_pit.LeftWall.L,
            'L2': self.foundation_pit.RightWall.L,
            'wl': dict(wl.as_coefficients_dict()),
            'wr': dict(wr.as_coefficients_dict()),
            'symbol': z
        }
        return self._save_cal_result(obj)
    
    def _save_cal_result(self, obj: dict) -> str:
        dic = {}
        for key in obj:
            val = obj[key]
            if type(val) == dict:
                val = FoundationPitAnalysor._transfer_symbol_str(val)
            dic[key] = val
        return json.dumps(dic)
    
    @staticmethod
    def _transfer_symbol_str(result: dict):
        obj = {}
        for key in result:
            obj[str(key)] = result[key]
        return obj

    @staticmethod
    def GenerateCaclId():
        return str(int(time.time()))
