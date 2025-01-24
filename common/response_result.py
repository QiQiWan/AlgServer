# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 20:37
# @Author  : Zeeland
# @File    : response_result.py
# @Software: PyCharm

from enum import Enum
from rest_framework.response import Response
from typing import Optional, Union, Any, List


class ResponseMsg:
    SUCCESS = 'success'
    BAD_REQUEST = 'bad request'
    UNAUTHORIZED = 'unauthorized'
    FORBIDDEN = 'forbidden'
    NOT_FOUND = 'not found'
    SERVER_ERROR = 'server error'
    INPUT_ERROR = 'input error'
    WRONG_PASSWORD = 'wrong password or no exist'
    VALIDATION_ERROR = 'validation error'
    TOKEN_EXPIRATION = 'token expiration'
    EMPTY_FILE_ERROR = 'empty file error'
    API_ABANDONED_ERROR = 'api abandoned error'
    HTTP_METHOD_ERROR = 'http method error'


class ResponseCode(Enum):
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500
    INPUT_ERROR = 501
    WRONG_PASSWORD = 502
    VALIDATION_ERROR = 503
    TOKEN_EXPIRATION = 504
    EMPTY_FILE_ERROR = 505
    MISSING_PARAMETER_ERROR = 506
    API_ABANDONED_ERROR = 507


class ResponseResult:

    def __init__(self, data: Union[Any, None] = None, code: Enum = ResponseCode.SUCCESS,
                 msg: Optional[str] = ResponseMsg.SUCCESS):
        self.code = code.value
        self.msg = msg
        self.data = data

    def to_response(self):
        return Response(data={
            'code': self.code,
            'msg': self.msg,
            'data': self.data,
        })

    def to_paginated_response(self, **kwargs):
        """分页返回值"""
        return Response(data={
            'code': self.code,
            'msg': self.msg,
            'last': kwargs['last'],
            'previous_page': kwargs['previous_page'],
            'max_size': kwargs['max_size'],
            'total_elements': kwargs['total_elements'],
            'total_pages': kwargs['total_pages'],
            'data': self.data
        })
