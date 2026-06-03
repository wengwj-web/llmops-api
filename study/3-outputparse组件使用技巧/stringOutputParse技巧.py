#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/2 09:15
@Author : wwj
@File : stringOutputParse技巧.py
"""
from datetime import datetime

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

#1.编排prompt
prompt = ChatPromptTemplate.from_template("{query}")

#2.创建大语言模型
llm = ChatOpenAI(
    model="qwen2.5:1.5b",  # ✅ 具体的模型名
    openai_api_base="http://localhost:11434/v1",  # ✅ Ollama 的 OpenAI 兼容地址
    openai_api_key="ollama",  # ✅ 随便填，Ollama 不验证
    temperature=0.7
    # model="qwen2.5:1.5b",           # 或 qwen2.5:1.5b（如果内存不够）
    # base_url="http://localhost:11434",
    # temperature=0.7
)
#3. 创建字符串输出解析器
parser = StrOutputParser()

#4.解析大语言模型生成结果并解析
content = parser.invoke(llm.invoke(prompt.invoke({"query":"你好，你是？"})))
print(content)
