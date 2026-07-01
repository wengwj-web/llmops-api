#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/29 13:50
@Author : wwj
@File : provider_entity.py
"""

import os
from typing import Any

import yaml
from pydantic import BaseModel, Field

from internal.lib.helper import dynamic_import


class ProviderEntity(BaseModel):
    """服务提供商实体，映射的数据是providers.yaml里的每条记录"""

    name: str
    label: str
    description: str
    icon: str
    background: str
    category: str


class Provider(BaseModel):
    """服务提供商，在该类下，可以获取到该服务提供商的所有工具，描述图标等多个信息"""

    name: str
    position: str
    providers_entity: ProviderEntity
    tool_entity_map: dict[str, Any] = Field(default_factory=dict)
    tool_func_map: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._provider_init()

    class Config:
        protected_namespaces = ()

    def get_tool(self, tool_name: str) -> Any:
        return self.tool_func_map[tool_name]

    def get_tool_entity(self, tool_name: str) -> Any:
        return self.tool_entity_map[tool_name]

    def get_tool_entites(self) -> list[Any]:
        return list(self.tool_entity_map.values())

    def _provider_init(self):
        """服务提供商初始化函数"""
        from internal.code.tools.builtin_tools.entities import ToolEntity

        # 1.获取当前类的路径，计算的到对应服务提供商的地址/路径
        current_path = os.path.abspath(__file__)
        entities_path = os.path.dirname(current_path)
        provider_path = os.path.join(
            os.path.dirname(entities_path), "providers", self.name
        )

        # 2.组装获取positions.yaml数据
        positions_yaml_path = os.path.join(provider_path, "positions.yaml")
        with open(positions_yaml_path, encoding="utf-8") as f:
            positions_yaml_data = yaml.safe_load(f)

        # 3.循环读取位置信息获取服务提供商的工具名字
        for tool_name in positions_yaml_data:
            # 4.获取工具的yaml数据
            tool_yaml_path = os.path.join(provider_path, f"{tool_name}.yaml")
            with open(tool_yaml_path, encoding="utf-8") as f:
                tool_yaml_data = yaml.safe_load(f)

            # 5.将工具信息实体赋值填充到tool_entity_map中
            self.tool_entity_map[tool_name] = ToolEntity(**tool_yaml_data)

            # 6.动态导入对应的工具并填充到tool_func_map中
            self.tool_func_map[tool_name] = dynamic_import(
                f"internal.code.tools.builtin_tools.providers.{self.name}",
                tool_name,
            )
