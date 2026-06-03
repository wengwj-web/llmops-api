#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/1 16:26
@Author : wwj
@File : 3.消息提示模版拼接.py
"""
from langchain_core.prompts import ChatPromptTemplate

system_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "聊天机器人，我叫{username}")
])
human_chat_prompt = ChatPromptTemplate.from_messages([
    ("human", "{query}")
])
chat_prompt = system_chat_prompt + human_chat_prompt
print(chat_prompt.invoke({
    "username":"机器人",
    "query":"你好 你是"
}).to_string())