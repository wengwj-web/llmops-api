#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/7/1 09:10
@Author : wwj
@File : current_time.py
"""

from datetime import datetime
from typing import Any

from langchain_core.tools import BaseTool


class CurrentTimeTool(BaseTool):
    """一个用于获取当前时间的工具"""

    name: str = "current_time"
    description: str = "一个用于获取当前时间的工具"

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")


def current_time(**kwargs) -> BaseTool:
    return CurrentTimeTool()
