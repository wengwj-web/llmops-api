#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/2 11:00
@Author : wwj
@File : runableParallel使用技巧.py
"""
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()
# 1.编排prompt
joke_prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}的冷笑话,尽可能短一点")
poem_prompt = ChatPromptTemplate.from_template("请讲一个关于{subject}的诗,尽可能短一点")
# 2.创建大模型
llm = ChatOpenAI(model="qwen2.5:1.5b",openai_api_base="http://localhost:11434/v1",openai_api_key="ollama",temperature=0.7)
# 3.创建解析器
parser = StrOutputParser()
# 4.编排连
joke_chain = joke_prompt | llm | parser
poem_chain = poem_prompt | llm | parser
# 5.并行
# map_chain = RunnableParallel(joke=joke_chain,poem=poem_chain)
map_chain = RunnableParallel({
    "joke": joke_chain,
    "poem": poem_chain
})
res= map_chain.invoke({"subject":"程序员"})
print(res)