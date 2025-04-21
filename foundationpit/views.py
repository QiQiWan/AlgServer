'''
Author: EatRice
Email: i@eatrice.cn
Date: 2023-05-22 14:03:55
LastEditTime: 2023-05-23 17:40:34
LastEditors: EatRice
Description: 
'''

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
import json
import time
from common.response_result import ResponseResult, ResponseMsg
from broadcast_service import broadcast_service
from FoundationAlg import AlgService
from .models import FoundationCalculationTask


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])  # 确保没有身份验证
@csrf_exempt  # 防止 CSRF 影响匿名 API 访问
def hello_world(request):
    return ResponseResult(data="Hello World").to_response()


@api_view(["POST"])
def start_calc_task(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        params = json.loads(data)
        analysor = AlgService.FoundationPitAnalysor(params['foundationPit'])

        # 存数据库
        id = AlgService.FoundationPitAnalysor.generate_cacl_id()
        task = FoundationCalculationTask(calID=id, status=1,
                                         foundation_pit=data,
                                         result = '')
        task.save()
        broadcast_service.subscribe('calculate', _save_cal_result)
        broadcast_service.publish('calculate', analysor, id)
        # _save_cal_result(analysor, id)
        dic = {
            "taskResult": "The results are still being calculated!",
            "taskStatus": 1,
            "taskId": id
        }
        return ResponseResult(data=dic).to_response()
    return ResponseResult(data=ResponseMsg.HTTP_METHOD_ERROR).to_response()

@api_view(["GET"])
def get_calc_result(request):
    id = request.data['taskId']
    task = FoundationCalculationTask.objects.get(calID=id)
    status = task.status
    if status == 1:
        res = {
            "taskResult" : "The results are still being calculated!",
            "taskStatus": status,
            "taskId": id
        }
    else:
        res = {
            "taskResult": json.loads(task.result),
            "taskStatus": status,
            "taskId": id
        }
    return ResponseResult(data=res).to_response()

@api_view(["GET"])
def get_all_result(request):
    page = request.GET.get('page', 1)
    page_size = request.GET.get('pageSize', 10)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    tasks = FoundationCalculationTask.objects.all()
    end_index = min(end_index, len(tasks))
    tasks_list = []
    import time
    for i in range(start_index, end_index):
        status = "finished"
        time_local = time.localtime(int(tasks[i].calID))
        now = time.time()
        if tasks[i].status == 1:
            if now - int(tasks[i].calID) < 600000:
                status = "calculating"
            else:
                status = "failed"
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        task = {
            "taskId": tasks[i].calID,
            "taskType": "基坑围护结构热力图",
            "time": time_str,
            "status": status,
        }
        tasks_list.append(task)
    res = {
        "taskList": tasks_list
    }
    return ResponseResult(data=res).to_response()

@api_view(["POST"])
def get_mesh_result(request):
    id = request.data['taskId']
    task = FoundationCalculationTask.objects.get(calID=id)
    status = task.status
    if status == 1:
        res = {
            "taskResult" : "The results are still being calculated!",
            "taskStatus": status,
            "ts": time.time(),
            "taskId": id
        }
    if status == 2:
        foundation_pit = json.loads(task.foundation_pit)['foundationPit']
        L1 = foundation_pit['LeftWall']['L']    
        L2 = foundation_pit['RightWall']['L']
        result = json.loads(task.result)
        wl = result['wl']
        wr = result['wr']
        sp_resolu = request.data['meta']['spaceResolu']
        left_mesh_dict, right_mesh_dict = \
            AlgService.FoundationPitAnalysor.create_double_mesh(L1, L2, wl, wr, sp_resolu)
        
        res = {
            "ts": time.time(),
            "meta": {
                "spaceResolu": sp_resolu
            },
            "leftMesh": left_mesh_dict,
            "rightMesh": right_mesh_dict,
            "taskStatus": status,
            "taskId": id
        }
    return ResponseResult(data=res).to_response()

@api_view(["POST"])
def get_single_mesh(request):
    id = request.data['taskId']
    task = FoundationCalculationTask.objects.get(calID=id)
    status = task.status
    if status == 1:
        res = {
            "taskResult" : "The results are still being calculated!",
            "taskStatus": status,
            "ts": time.time(),
            "taskId": id
        }
    if status == 2:
        foundation_pit = json.loads(task.foundation_pit)['foundationPit']
        result = json.loads(task.result)
        side = request.data['side']
        if side == 0:
            L = foundation_pit['LeftWall']['L']
            w = result['wl']
        else:
            L = foundation_pit['RightWall']['L']
            w = result['wr']
        sp_resolu = request.data['meta']['spaceResolu']

        wall_mesh = \
            AlgService.FoundationPitAnalysor.create_single_mesh(L, w, sp_resolu, side)
        
        res = {
            "ts": time.time(),
            "x_Range": [0, L],
            "xGridSize": L / sp_resolu,
            "yRange": [wall_mesh['minDeformation'], wall_mesh['maxDeformation']],
            "yGridSize": 0,
            "value": wall_mesh['mesh'],
            "meshShape": wall_mesh['shape'],
            "taskStatus": status,
            "taskId": id
        }
    return ResponseResult(data=res).to_response()

def _save_cal_result(analysor: AlgService.FoundationPitAnalysor,
                     id: str):
    json = analysor.calculate(id)
    task = FoundationCalculationTask.objects.get(calID=id)
    task.status = 2
    task.result = json
    task.save()
    broadcast_service.publish('polling')
