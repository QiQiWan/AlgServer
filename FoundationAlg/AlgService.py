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
        params_dict = json.loads(queries)
        try:
            self.check_params(params_dict)
        except Exception as err:
            raise err
        self.foundation_pit = self.create_foundation(params_dict)

    def check_params(self, queries: dict):
        # 检查构造一个基坑对象所需要的所有参数
        para_list = ['LeftWall', 'RightWall', 'H1', 'H2', 'ExcaveDeepth',\
                    'SupportCount', 'Supports', 'B', 'D', 'BoreHole', 'AverageSoil',\
                    'ds', 'Palim', 'Pplim', 'PalimWl', 'PplimWl', 'PalimWr', 'PplimWr',\
                    'LeftOverLoad', 'RightOverLoad', 'LeftStrengthLoad', 'RightStrengthLoad']
        for item in para_list:
            if item not in queries:
                raise Exception(f'The argument {item} is not found!')

        # 对某些复杂参数进行进一步检查
        support_list = ['Material', 'SpaceLength', 'N']
        for item in support_list:
            if item not in queries['Supports'][0]:
                raise Exception(f'The arguement {item} in support is not found!')

        # 对两侧的支护桩参数进行检查
        pile_list = ['L', 'h', 'Material', 'I', 'E', 'EI', 'kar', 'G', 'H']
        for item in pile_list:
            if item not in queries['LeftWall']:
                raise Exception(f'The argument {item} in LeftWall is not found!')
            if item not in queries['RightWall']:
                raise Exception(f'The argument {item} in RightWall is not found!')

        # 对土层钻孔数据格式进行检查
        soil_list = ['soil', 'interval']
        for item in soil_list:
            if item not in queries['BoreHole'][0]:
                raise Exception(f'The argument {item} in borehole is not Found!')
        
        # 检查土层的深度必须大于等于支护桩的长度
        l = len(queries['BoreHole'])
        bottom = queries['BoreHole'][l - 1]['interval']['bottom']
        if bottom < queries['LeftWall']['L'] or bottom < queries['RightWall']['L']:
            raise Exception(f'The bottom of the soil layers is less than the pile!')
        
        return True

    def create_foundation(self, queries: dict):
        return FoundationPit.loads(queries)

    def calculate(self, id, hm=10):
        self.ID = id
        z = EnergyMethodSolver.init_symbol()
        solver = EnergyMethodSolver(z, self.foundation_pit, hm=hm)
        _, wl, wr = solver.solve()
        obj = {
            'ID': id,
            'L1': self.foundation_pit.left_wall.L,
            'L2': self.foundation_pit.right_wall.L,
            'wl': dict(wl.as_coefficients_dict()),
            'wr': dict(wr.as_coefficients_dict()),
            'symbol': str(z)
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
            obj[str(key)] = float(result[key])
        return obj

    @staticmethod
    def generate_cacl_id():
        return str(int(time.time()))
