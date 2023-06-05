# -*- coding: utf-8 -*-
# @Time    : 2023/3/30 20:55
# @Author  : Zeeland
# @File    : interceptor.py
# @Software: PyCharm
# @Description: 异常事件拦截器

import json
import logging
from abc import ABC
from typing import Union
from rest_framework.exceptions import APIException, ValidationError
from Common.response_result import ResponseMsg, ResponseCode, ResponseResult



logger = logging.getLogger(__name__)


class CustomBaseException(Exception, ABC):
    """自定义异常都需要继承这个类，继承了之后在报错之后接口可以返回更加详细的信息"""

    code: ResponseCode
    message: Union[ResponseMsg, str]


class APIError(CustomBaseException):
    def __init__(self):
        self.code = ResponseCode.SERVER_ERROR
        self.message = ResponseMsg.SERVER_ERROR


class InputError(CustomBaseException):
    def __init__(self, data:str):
        self.code = ResponseCode.INPUT_ERROR
        self.message = data


class WrongPasswordError(CustomBaseException):
    def __init__(self):
        self.code = ResponseCode.WRONG_PASSWORD
        self.message = ResponseMsg.WRONG_PASSWORD


class TokenExpirationError(CustomBaseException):
    def __init__(self):
        self.code = ResponseCode.TOKEN_EXPIRATION
        self.message = ResponseMsg.TOKEN_EXPIRATION


class EmptyFileError(CustomBaseException):
    def __init__(self):
        self.code = ResponseCode.EMPTY_FILE_ERROR
        self.message = ResponseMsg.EMPTY_FILE_ERROR


class MissingParameterError(CustomBaseException):
    def __init__(self, param_name: str):
        self.code = ResponseCode.MISSING_PARAMETER_ERROR
        self.message = f"lost parameter: {param_name}"


class APIAbandonedError(CustomBaseException):
    def __init__(self, api_name: str):
        self.code = ResponseCode.API_ABANDONED_ERROR
        self.message = f"[{ResponseMsg.API_ABANDONED_ERROR}] API {api_name} has been abandoned."


def custom_exception_handler(exc, context):
    """
    统一异常处理，执行接口报错的时候会调用此函数

    Args:
        exc: 异常基本信息
        context:
        {
            'view': <app.views.WrappedAPIView object at 0x000001B49FB8FC08>,
            'args': (),
            'kwargs': {},
            'request': <rest_framework.request.Request: POST '/user/login/'>
        }

    Returns:
        ResponseResult封装的结果集
    """
    if issubclass(type(exc), CustomBaseException):
        code = exc.code
        msg = exc.message
    elif isinstance(exc, ValidationError):
        code = ResponseCode.VALIDATION_ERROR
        msg = f"{ResponseMsg.VALIDATION_ERROR} [more information] {context} " \
              f"| May be has exist the same object or foreign key that does not exist. Please check again."
    else:
        code = ResponseCode.SERVER_ERROR
        msg = f"{type(exc)} {str(exc)}"
    logger.error(f"Exception interceptor | [code]{code}  [msg]{msg}")
    return ResponseResult(code=code, msg=msg).to_response()

