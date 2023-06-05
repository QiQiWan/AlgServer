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
from Common.response_result import ResponseResult, ResponseMsg
from models import FoundationCalculationTask


@api_view(["POST"])
def startCaclTask(request):
    if request.method == 'POST':
        data = request.body
        # params = json.loads(data)
        analysor, result = AlgService.FoundationPitAnalysor(data)
        if not result:
            dic = {
                "Message" : analysor,
                "Status": "Fail"
            }
            return ResponseResult(data=dic).to_response()
        # 存数据库
        id = AlgService.FoundationPitAnalysor.GenerateCaclId()
        foundation_pit = analysor.foundation_pit.ToDict()
        task = FoundationCalculationTask(id=id, status=1,
                                         foundation_pit=foundation_pit,
                                         result = '')
        task.save()
        broadcast_service.subscribe('calculate', _save_cal_result)
        broadcast_service.publish('calculate', id)
        dic = {
            "TaskID": id,
            "Status": "Waiting"
        }
        return ResponseResult(data=dic).to_response()
    return ResponseResult(data=ResponseMsg.HTTP_METHOD_ERROR).to_response()

def _save_cal_result(analysor: AlgService.FoundationPitAnalysor,
                     id: str):
    json = analysor.calculate()
    task = FoundationCalculationTask.objects.get(id=id)
    task.status = 2
    task.result = json


def getCaclResult(request):
    id = request['id']
    task = FoundationCalculationTask.objects.get(id=id)
    return ResponseResult(data=task.result).to_response()