#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/5/23 1:55
@Author  : thezehui@gmail.com
@File    : 1.缓冲窗口记忆示例.py
"""
from operator import itemgetter

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.创建提示模板&记忆
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是OpenAI开发的聊天机器人，请根据对应的上下文回复用户问题"),
    MessagesPlaceholder("history"),
    ("human", "{query}"),
])

# 用 InMemoryChatMessageHistory 替代 ConversationTokenBufferMemory
history_store = InMemoryChatMessageHistory()

def load_memory_variables(_):
    """模拟旧版 memory.load_memory_variables 的返回格式"""
    return {"history": history_store.messages}

def save_memory_variables(inputs, output):
    """模拟旧版 memory.save_context"""
    history_store.add_user_message(inputs["query"])
    history_store.add_ai_message(output)

# 2.创建大语言模型
llm = ChatOpenAI(
    model="qwen2.5:1.5b",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    temperature=0.7
)

# 3.构建链应用
chain = RunnablePassthrough.assign(
    history=RunnableLambda(load_memory_variables) | itemgetter("history")
) | prompt | llm | StrOutputParser()

# 4.死循环构建对话命令行
while True:
    query = input("Human: ")

    if query == "q":
        exit(0)

    chain_input = {"query": query, "language": "中文"}

    response = chain.stream(chain_input)
    print("AI: ", flush=True, end="")
    output = ""
    for chunk in response:
        output += chunk
        print(chunk, flush=True, end="")
    save_memory_variables(chain_input, output)
    print("")
    print("history: ", load_memory_variables({}))