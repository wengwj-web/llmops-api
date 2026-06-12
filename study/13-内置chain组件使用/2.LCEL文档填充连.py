#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/11 16:16
@Author : wwj
@File : 2.LCEL文档填充连.py
"""

import dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

prompt = ChatPromptTemplate.format_messages([
    {"system","你是聊天机器人，根据用户提供上下文回复用户问题：\n\n<context>{context}</context>"},
    {"human":"{query}"}
])

llm = ChatOpenAI(model="qwen2.5:1.5b",openai_api_base="http://localhost:11434/v1",openai_api_key="ollama",temperature=0.7)

chain = create_stuff_documents_chain(prompt=prompt,llm=llm)

documents = [
    Document(page_content="小明喜欢绿色，但不喜欢黄色"),
    Document(page_content="小王喜欢粉色，也有一点喜欢红色"),
    Document(page_content="小泽喜欢蓝色，但更喜欢青色")
]

content = chain.invoke({"query":"统计下大家喜欢什么颜色","context":documents})
print(content)