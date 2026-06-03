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

# 2.创建连
chain = prompt | llm | parser

# 3.调用连
print(chain.invoke({"query":"讲程序员冷笑话"}))