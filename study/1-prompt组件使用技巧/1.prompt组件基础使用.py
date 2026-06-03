#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/1 16:02
@Author : wwj
@File : 1.prompt组件基础使用.py
"""
import datetime

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder

prompt=PromptTemplate.from_template("请讲关于{subject}的冷笑话")
print(prompt.format(subject="程序员"))
prompt_value = prompt.invoke({"subject":"程序员"})
print(prompt_value.to_string())
print(prompt_value.to_messages())

print("==========================")

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "聊天机器人,当前时间是:{now}"),
    MessagesPlaceholder("chat_history"),
    HumanMessagePromptTemplate.from_template("请讲关于{subject}的冷笑话")
]).partial(now=datetime.datetime.now())


chat_from_value = chat_prompt.invoke({
    # "now": datetime.datetime.now(),
    "chat_history": [
        ("human","hello"),
        AIMessage("我是chatgpt")
    ],
    "subject": "程序员"
})
print(chat_from_value)
print(chat_from_value.to_string())