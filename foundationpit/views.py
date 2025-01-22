'''
Author: EatRice
Email: i@eatrice.cn
Date: 2023-05-22 14:03:55
LastEditTime: 2023-05-23 17:40:34
LastEditors: EatRice
Description: 
'''

import json
import time
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from broadcast_service import broadcast_service
from FoundationAlg import AlgService
from common.response_result import ResponseResult, ResponseMsg
from .models import FoundationCalculationTask

@api_view(["GET"])
@permission_classes([AllowAny])  # 允许任何人访问
def hello_world(request):
    return ResponseResult(data="Hello World").to_response()

@api_view(["POST"])
@permission_classes([AllowAny])  # 允许任何人访问
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

@api_view(["POST"])
@permission_classes([AllowAny])  # 允许任何人访问
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

@api_view(["POST"])
@permission_classes([AllowAny])  # 允许任何人访问
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
            AlgService.FoundationPitAnalysor.create_mesh(L1, L2, wl, wr, sp_resolu)
        
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

def _save_cal_result(analysor: AlgService.FoundationPitAnalysor,
                     id: str):
    json = analysor.calculate(id)
    task = FoundationCalculationTask.objects.get(calID=id)
    task.status = 2
    task.result = json
    task.save()
    broadcast_service.publish('polling')
