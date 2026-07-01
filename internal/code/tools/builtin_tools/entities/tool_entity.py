#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/29 13:59
@Author : wwj
@File : tool_entity.py
"""

from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field


class ToolParamType(str, Enum):
    """工具参数类型枚举类"""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"


class toolParam(BaseModel):
    """工具参数类型"""

    name: str
    label: str
    type: ToolParamType
    required: bool = False
    default: Optional[Any] = None
    min: Optional[float] = None
    max: Optional[float] = None
    options: list[dict[str, Any]] = Field(default_factory=list)


class ToolEntity(BaseModel):
    """工具实体类，存储的信息映射的是工具名，yaml里的数据"""

    name: str
    label: str
    description: str
    params: list[toolParam] = Field(default_factory=list)
