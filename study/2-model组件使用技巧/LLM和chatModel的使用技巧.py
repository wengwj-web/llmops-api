#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/1 17:04
@Author : wwj
@File : LLM和chatModel的使用技巧.py
"""
from datetime import datetime

import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

dotenv.load_dotenv()

#1.编排prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是聊天机器人，时间为：{now}"),
    ("human", "{query}")
]).partial(now=datetime.now())

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

# ai_message = llm.invoke(
#     prompt.invoke({ "query": "现在是几点"})
# )

# ai_message = llm.batch([
#     prompt.invoke({ "query": "现在是几点"}),
#     prompt.invoke({ "query": "讲一个程序员的冷笑话"})
# ])
#
# for item in ai_message:
#     print(item.content)
#     print("===========")

response = llm.stream(
    prompt.invoke({"query": "介绍下自己"})
)

for chunk in response:
    print(chunk.content,flush=True,end='')