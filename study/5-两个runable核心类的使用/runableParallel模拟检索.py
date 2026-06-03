#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/2 11:00
@Author : wwj
@File : runableParallel使用技巧.py
"""
from operator import itemgetter

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()
def retrieval(query:str):
    """模拟检索器函数"""
    print("正在检索:", query)
    return "机器人"
# 1.编排prompt
prompt = ChatPromptTemplate.from_template("""请根据用户问题回答，可以参考对应的上下文进行生成，

<context>
{context}
</context>

用户提问的是：{query}""")
# 2.创建大模型
llm = ChatOpenAI(model="qwen2.5:1.5b",openai_api_base="http://localhost:11434/v1",openai_api_key="ollama",temperature=0.7)
# 3.创建解析器
parser = StrOutputParser()

# 4.编排连
chain = {
    "context": lambda x: retrieval(x["query"]),
    "query": itemgetter("query"),
}| prompt | llm | parser
# 5.调用连
content = chain.invoke({"query":"你好，你是谁？"})
print(content)