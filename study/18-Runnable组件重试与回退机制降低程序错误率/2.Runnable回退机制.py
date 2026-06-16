#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/6 11:37
@Author  : thezehui@gmail.com
@File    : 2.Runnable回退机制.py
"""
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.构建prompt与LLM，并将model切换为gpt-3.5-turbo-18k引发出错
prompt = ChatPromptTemplate.from_template("{query}")
llm = ChatOpenAI( model="ERNIE-Bot").with_fallbacks([
    ChatOpenAI(model="qwen2.5:1.5b",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    temperature=0.7,)
])

# 2.构建链应用
chain = prompt | llm | StrOutputParser()

# 3.调用链并输出结果
content = chain.invoke({"query": "你好，你是?"})
print(content)
