from .NewFoundationPit import *
from .UpdateEnergy import EnergyMethodSolver
import json
import time

# Create your models here.
class FoundationPitAnalysor(object):

    def __init__(self, params_dict):
        """生成一个基坑计算参数模型，调度计算任务，生成任务ID

        Args:
            queries (str): 基坑计算参数列表，是一个json文件
        """
        try:
            foundation_pit = self.check_params(params_dict)
        except Exception as err:
            raise err
        self.foundation_pit = self.create_foundation(foundation_pit)

    def check_params(self, queries: dict):
        # 检查构造一个基坑对象所需要的所有参数
        para_list = ['LeftWall', 'RightWall', 'ExcavaDepth',
                    'SupportCount', 'Supports', 'B', 'D', 'BoreHole', 'AverageSoil',
                    'ds', 'Palim', 'Pplim', 'PalimWl', 'PplimWl', 'PalimWr', 'PplimWr',
                    'LeftOverLoad', 'RightOverLoad', 'LeftStrengthLoad', 'RightStrengthLoad']
        for item in para_list:
            if item not in queries:
                raise Exception(f'The argument {item} is not found!')

        # 对水平支撑参数进行进一步检查
        support_list = ['Material', 'SpaceLength', 'N']
        for item in support_list:
            if item not in queries['Supports'][0]:
                raise Exception(f'The arguement {item} in support is not found!')

        # 对两侧的支护桩参数进行检查
        pile_list = ['L', 'h', 'Material', 'I', 'EI', 'kar', 'G']
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
        
        return queries

    def create_foundation(self, queries: dict):
        return FoundationPit.loads(queries)

    def calculate(self, id, hm=10):
        self.ID = id
        z = EnergyMethodSolver.init_symbol()
        solver = EnergyMethodSolver(z, self.foundation_pit, hm=hm)
        _, wl, wr = solver.solve()
        cwl = {str(k): v for k, v in wl.as_coefficients_dict().items()}
        cwr = {str(k): v for k, v in wr.as_coefficients_dict().items()}
        obj = {
            'ID': id,
            'L1': self.foundation_pit.left_wall.L,
            'L2': self.foundation_pit.right_wall.L,
            'wl': dict(sorted(cwl.items())),
            'wr': dict(sorted(cwr.items())),
            'symbol': str(z)
        }
        return self._save_cal_result(obj)
    
    @staticmethod
    def create_double_mesh(L1, L2, wl, wr, resolution: int):
        L1 = L1
        L2 = L2
        zl_seq, left_center_column = FoundationPitAnalysor.cal_center_column(L1, wl, resolution)
        zr_seq, right_center_column = FoundationPitAnalysor.cal_center_column(L2, wr, resolution)
        
        
        expand_left_column = FoundationPitAnalysor.create_mesh(L1, wl, zl_seq, 
                                                                      left_center_column, resolution)
        expand_right_column = FoundationPitAnalysor.create_mesh(L2, wr, zr_seq, 
                                                                       right_center_column,  resolution)

        left_mesh_dict = {
            "mesh": expand_left_column.tolist(),
            "z_seq": zl_seq,
            "shape": expand_left_column.shape,
            "maxDeformation": max(left_center_column),
            "minDeformation": min(left_center_column)
        }
        right_mesh_dict = {
            "mesh": expand_right_column.tolist(),
            "z_seq": zr_seq,
            "shape": expand_right_column.shape,
            "maxDeformation": max(right_center_column),
            "minDeformation": min(right_center_column)
        }
        return left_mesh_dict, right_mesh_dict
    
    @staticmethod
    def create_single_mesh(L, w, resolution: int, side: int):
        seq, center_column = FoundationPitAnalysor.cal_center_column(L, w, resolution)
        mesh = FoundationPitAnalysor.create_mesh(L, w, seq, center_column, resolution)
        mesh_dict = {
            "mesh": mesh.tolist(),
            "z_seq": center_column[0],
            "shape": mesh.shape,
            "maxDeformation": max(center_column),
            "minDeformation": min(center_column),
            "side": side
        }
        return mesh_dict
    
    @staticmethod
    def create_mesh(L, w, seq, center_coulomn, resolution: int):

        expand_column = []
        resolution = resolution * 10
        half_reso = resolution // 2
        if resolution % 2 == 0:
            half_reso -= 1
        
        for i in range(half_reso):
            dis = half_reso - i
            coef_reduce = FoundationPitAnalysor.cal_distance_coeff(
                FoundationPitAnalysor.parabola_distance_func, dis, resolution // 2)
        
            new_column = []
            for j in range(len(center_coulomn)):
                new_column.append(center_coulomn[j] * coef_reduce)
            expand_column.append(new_column)

        expand_column.append(center_coulomn)
        if resolution % 2 == 0:
            expand_column.append(center_coulomn)
            
        for i in range(half_reso):
            expand_column.append(expand_column[half_reso - i - 1][:])

        from numpy import array
        return array(expand_column).transpose()

    @staticmethod
    def cal_center_column(L: float, wf: dict, resolution: int):
        center_column = []
        z_seq = []
        for i in range(resolution * 10):
            x = i * L / resolution / 10
            mutil = 1
            defor = 0
            wf_coeffs = wf.values()
            for wf_coeff in wf_coeffs:
                if defor == 0:
                    defor += wf_coeff
                else:
                    mutil *= x
                    defor += wf_coeff * mutil

            center_column.append(defor)
            z_seq.append(x)
        z_seq[-1] = L
        return z_seq, center_column
    
    @staticmethod
    def cal_distance_coeff(func, dis: int, max_dis: int):
        return func(dis / max_dis)
    
    @staticmethod
    def linear_distance_func(x: float):
        return -0.9 * x + 1
    
    @staticmethod
    def parabola_distance_func(x: float):
        return -0.9 * x * x + 1

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
