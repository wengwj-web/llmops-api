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
