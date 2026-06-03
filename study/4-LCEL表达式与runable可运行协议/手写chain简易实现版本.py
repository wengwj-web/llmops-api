#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/2 10:21
@Author : wwj
@File : 手写chain简易实现版本.py
"""
from typing import Any

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.构建组件
prompt = ChatPromptTemplate.from_template("{query}")
llm = ChatOpenAI(model="qwen2.5:1.5b",openai_api_base="http://localhost:11434/v1",openai_api_key="ollama",temperature=0.7)
parser = StrOutputParser()

# 2.定义连
class Chain:
    steps: list = []

    def __init__(self, steps):
        self.steps = steps

    def invoke(self, input: Any) -> Any:
        for step in self.steps:
            input = step.invoke(input)
            print("步骤：", step)
            print("输出：", input)
            print("=============")
        return input
# 3.编排连
chain = Chain([prompt,llm,parser])

# 4.调用输出结果
print(chain.invoke({"query":"你好，你是？"}))