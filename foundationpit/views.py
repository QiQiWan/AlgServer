'''
Author: EatRice
Email: i@eatrice.cn
Date: 2023-05-22 14:03:55
LastEditTime: 2023-05-23 17:40:34
LastEditors: EatRice
Description: 
'''

import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from broadcast_service import broadcast_service
from FoundationAlg import AlgService
from common.response_result import ResponseResult, ResponseMsg
from .models import FoundationCalculationTask

@api_view(["GET"])
def hello_world(request):
    return ResponseResult(data="Hello World").to_response()

@api_view(["POST"])
def start_calc_task(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        # params = json.loads(data)
        analysor = AlgService.FoundationPitAnalysor(data)

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
            "task_result": "The results are still being calculated!",
            "task_status": 1,
            "task_id": id
        }
        return ResponseResult(data=dic).to_response()
    return ResponseResult(data=ResponseMsg.HTTP_METHOD_ERROR).to_response()

@api_view(["POST"])
def get_calc_result(request):
    id = request.data['task_id']
    task = FoundationCalculationTask.objects.get(calID=id)
    status = task.status
    if status == 1:
        res = {
            "task_result" : "The results are still being calculated!",
            "task_status": status,
            "task_id": id
        }
    else:
        res = {
            "task_result": json.loads(task.result),
            "task_status": status,
            "task_id": id
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
