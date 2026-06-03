#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/5/29 16:02
@Author : wwj
@File : exception.py
"""
from dataclasses import field
from typing import Any

from pkg.response import HttpCode


class CustomException(Exception):
    """基础自定义异常信息"""
    code: HttpCode = HttpCode.FAIL
    message: str = ""
    data: Any = field(default_factory=dict)
    def __init__(self,message:str="",data:Any=None):
        super().__init__()
        self.message = message
        self.data = data

class FailException(CustomException):
    """通用自定义异常"""
    pass

class NotFoundException(CustomException):
    code: HttpCode.NOT_FOUND

class UnauthorizedException(CustomException):
    code: HttpCode.UNAUTHORIZED

class ForbiddenException(CustomException):
    code: HttpCode.FORBIDDEN

class ValidationException(CustomException):
    code: HttpCode.VALIDATION_ERROR