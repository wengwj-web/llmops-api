#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/8 16:53
@Author  : thezehui@gmail.com
@File    : google_serp_tool.py
"""

import dotenv
import os
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from pydantic import BaseModel, Field

dotenv.load_dotenv()
print("SERPER_API_KEY:", os.getenv("SERPER_API_KEY"))


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


google_serper = GoogleSerperRun(
    name="google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)

print(google_serper.invoke("马拉松的世界记录是多少?"))
