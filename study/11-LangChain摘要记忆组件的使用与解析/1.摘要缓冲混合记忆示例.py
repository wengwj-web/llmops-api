#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/5/23 1:55
@Author  : thezehui@gmail.com
@File    : 1.摘要缓冲混合记忆示例.py
"""
from operator import itemgetter

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint

dotenv.load_dotenv()


class ConversationSummaryBufferMemory:
    """新版手动实现摘要缓冲混合记忆，兼容旧版逻辑"""

    def __init__(self, llm, max_token_limit=300, return_messages=True, input_key="query"):
        self.llm = llm
        self.max_token_limit = max_token_limit
        self.return_messages = return_messages
        self.input_key = input_key
        self.messages = []
        self.summary = ""

    def _count_tokens(self, messages):
        """估算 token 数"""
        total = 0
        for msg in messages:
            content = msg.content if hasattr(msg, "content") else str(msg)
            total += len(content) * 0.5
        return int(total)

    def _summarize(self, messages_to_summarize):
        """对旧消息进行摘要"""
        if not messages_to_summarize:
            return ""

        # 构建摘要提示
        summary_prompt = f"请将以下对话内容总结为简洁的摘要：\n\n"
        for msg in messages_to_summarize:
            role = "Human" if isinstance(msg, HumanMessage) else "AI"
            summary_prompt += f"{role}: {msg.content}\n"
        summary_prompt += "\n摘要："

        # 调用 LLM 生成摘要
        try:
            response = self.llm.invoke(summary_prompt)
            return response.content if hasattr(response, "content") else str(response)
        except:
            # 如果摘要失败，直接拼接内容
            return "; ".join([msg.content[:50] for msg in messages_to_summarize])

    def _trim_and_summarize(self):
        """当超过 token 限制时，对旧消息摘要，保留最近对话"""
        # 如果总 token 未超限，不处理
        if self._count_tokens(self.messages) <= self.max_token_limit:
            return

        # 分离 system 消息（如果有）
        system_msgs = [m for m in self.messages if isinstance(m, SystemMessage)]
        other_msgs = [m for m in self.messages if not isinstance(m, SystemMessage)]

        # 从旧到新尝试找到需要摘要的消息
        # 策略：保留最近一轮对话，其余摘要
        if len(other_msgs) >= 4:  # 至少有两轮对话 (human+ai) * 2
            # 保留最近一轮
            keep_msgs = other_msgs[-2:]  # 最近 human + ai
            summarize_msgs = other_msgs[:-2]  # 其余需要摘要

            # 生成摘要
            new_summary = self._summarize(summarize_msgs)
            if self.summary:
                self.summary = f"{self.summary}; {new_summary}"
            else:
                self.summary = new_summary

            # 重建消息列表
            self.messages = system_msgs + [SystemMessage(content=f"历史摘要：{self.summary}")] + keep_msgs

    def load_memory_variables(self, inputs):
        """加载记忆变量"""
        self._trim_and_summarize()
        return {"history": self.messages if self.return_messages else []}

    def save_context(self, inputs, outputs):
        """保存对话上下文"""
        query = inputs.get(self.input_key, "")
        output = outputs.get("output", "")

        self.messages.append(HumanMessage(content=query))
        self.messages.append(AIMessage(content=output))

        self._trim_and_summarize()


# 1.创建提示模板&记忆
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是OpenAI开发的聊天机器人，请根据对应的上下文回复用户问题"),
    MessagesPlaceholder("history"),
    ("human", "{query}"),
])

# 2.创建大语言模型
llm = ChatOpenAI(
    model="qwen2.5:1.5b",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    temperature=0.7
)

# 创建记忆（max_token_limit=300，超过时生成摘要）
memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=300,
    return_messages=True,
    input_key="query"
)

# 3.构建链应用
chain = RunnablePassthrough.assign(
    history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
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
    memory.save_context(chain_input, {"output": output})
    print("")
    print("history: ", memory.load_memory_variables({}))