'''
Author: EatRice
Email: i@eatrice.cn
Date: 2023-05-22 14:03:55
LastEditTime: 2023-05-23 18:42:07
LastEditors: EatRice
Description: 
'''

from django.db import models
from FoundationAlg import *

class FoundationCalculationTask(models.Model):
    calID = models.CharField(primary_key=True, max_length=12)
    statusChoice = (
        (1, "计算中"),
        (2, "计算完成")
    )
    status = models.IntegerField("计算状态", default=1, null=True, blank=True, choices=statusChoice)
    foundation_pit = models.JSONField("基坑计算参数")
    result = models.JSONField("计算结果")
    
    
