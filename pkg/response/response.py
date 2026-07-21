#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/5/29 15:22
@Author : wwj
@File : response.py
"""

from dataclasses import field, dataclass
from email import message
from typing import Any, Union, Generator

from flask import jsonify, stream_with_context, Response as FlaskResponse
from .http_code import HttpCode


@dataclass
class Response:
    """基础httpcode相应格式"""

    code: HttpCode = HttpCode.SUCCESS
    message: str = ""
    data: Any = field(default_factory=dict)


def json(data: Response = None):
    """基础的相应接口"""
    return jsonify(data), 200


def success_json(data: Any = None):
    return json(Response(code=HttpCode.SUCCESS, message="", data=data))


def fail_json(data: Any = None):
    return json(Response(code=HttpCode.FAIL, message="", data=data))


def validate_error_json(errors: dict = None):
    first_key = next(iter(errors))
    if first_key is not None:
        msg = errors.get(first_key)[0]
    else:
        msg = ""
    return json(Response(code=HttpCode.VALIDATION_ERROR, message=msg, data=errors))


def message(code: HttpCode = None, msg: str = ""):
    return json(Response(code=code, message=msg, data={}))


def success_message(msg: str = ""):
    return message(code=HttpCode.SUCCESS, msg=msg)


def fail_message(msg: str = ""):
    return message(code=HttpCode.FAIL, msg=msg)


def not_found_message(msg: str = ""):
    return message(code=HttpCode.NOT_FOUND, msg=msg)


def unauthorized_message(msg: str = ""):
    return message(code=HttpCode.UNAUTHORIZED, msg=msg)


def forbidden_message(msg: str = ""):
    return message(code=HttpCode.FORBIDDEN, msg=msg)


def compact_generate_response(response: Union[Response, Generator]) -> FlaskResponse:
    """统一合并处理块输出以及流式事件输出"""
    # 1.检测下是否为块输出(Response)
    if isinstance(response, Response):
        return json(response)
    else:
        # 2.response格式为生成器，代表本次响应需要执行流式事件输出
        def generate() -> Generator:
            """构建generate函数，流式从response中获取数据"""
            yield from response

        # 3.返回携带上下文的流式事件输出
        return FlaskResponse(
            stream_with_context(generate()),
            status=200,
            mimetype="text/event-stream",
        )
