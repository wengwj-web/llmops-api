#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/5/29 15:20
@Author : wwj
@File : http_code.py
"""
from enum import Enum


class HttpCode(str, Enum):
    """http基础业务状态码"""
    SUCCESS = "Success"
    FAIL="Fail"
    NOT_FOUND="Not Found"
    UNAUTHORIZED="Unauthorized"
    FORBIDDEN="Forbidden"
    VALIDATION_ERROR="Validation Error"