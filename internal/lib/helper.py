#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/30 15:18
@Author : wwj
@File : helper.py
"""

import importlib
from typing import Any


def dynamic_import(module_name: str, symbol_name: str) -> Any:
    module = importlib.import_module(module_name)
    return getattr(module, symbol_name)


def add_attribute(attr_name: str, attr_value: Any):
    """装饰器函数，为特定的函数添加相应的属性，第一个参数为属性名字，第二个参数为属性值"""

    def decorator(func):
        setattr(func, attr_name, attr_value)
        return func

    return decorator
