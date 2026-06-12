#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/11 15:42
@Author : wwj
@File : 1.LLMchain使用技巧.py
"""
import dotenv
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}的冷笑话")

llm = ChatOpenAI(model="qwen2.5:1.5b",openai_api_base="http://localhost:11434/v1",openai_api_key="ollama",temperature=0.7)

chain = LLMChain(llm=llm,prompt=prompt)

print(chain("程序员"))
print(chain.run("程序员"))
print(chain.apply([{"subject": "程序员"}]))
print(chain.generate([{"subject": "程序员"}]))
print(chain.predict(subject="程序员"))