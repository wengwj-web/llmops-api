#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/4 17:10
@Author  : thezehui@gmail.com
@File    : 1.多LLM链选择示例.py
"""
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.创建提示模板&定义默认大语言模型
prompt = ChatPromptTemplate.from_template("{query}")
llm = ChatOpenAI(model="gpt-3.5-turbo-16k").configurable_alternatives(
    ConfigurableField(id="llm"),
    default_key="gpt-3.5",
    gpt4=ChatOpenAI(model="gpt-4o"),
    wenxin= ChatOpenAI(
        model="ERNIE-Bot",
        base_url="https://qianfan.baidubce.com/v2",
        temperature=0.7
    ),
    qwen=ChatOpenAI(
        model="qwen2.5:1.5b",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        temperature=0.7
    ),
)

# 2.构建链应用
chain = prompt | llm | StrOutputParser()

# 3.调用链并传递配置信息，并切换到文心一言模型或者gpt4模型
content = chain.invoke(
    {"query": "你好，你是什么模型呢?"},
    config={"configurable": {"llm": "qwen"}}
)
print(content)
