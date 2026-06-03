#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/2 13:59
@Author : wwj
@File : 回调功能使用技巧.py
"""
import time
from typing import Any, Optional, Union
from uuid import UUID

import dotenv
from langchain_core.callbacks import StdOutCallbackHandler, BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.outputs import GenerationChunk, ChatGenerationChunk, LLMResult
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

class LLMOpsCallbackHander(BaseCallbackHandler):
    """自定义LLMops回调处理器"""

    start_at:float = 0

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        print("聊天模型开始进行")
        print("serialized", serialized)
        print("messages", messages)
        self.start_at = time.time()

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        end_at = time.time()
        print("完整输出", response)
        print("程序消耗：", end_at - self.start_at)

    # def on_llm_new_token(
    #     self,
    #     token: str,
    #     *,
    #     chunk: Optional[Union[GenerationChunk | ChatGenerationChunk]] = None,
    #     run_id: UUID,
    #     parent_run_id: Optional[UUID] = None,
    #     **kwargs: Any,
    # ) -> Any:
    #     print("token生成了")
    #     print("token", token)


def retrieval(query:str):
    """模拟检索器函数"""
    print("正在检索:", query)
    return "机器人"
# 1.编排prompt
prompt = ChatPromptTemplate.from_template("{query}")
# 2.创建大模型
llm = ChatOpenAI(model="qwen2.5:1.5b",openai_api_base="http://localhost:11434/v1",openai_api_key="ollama",temperature=0.7)
# 3.创建解析器
parser = StrOutputParser()

# 4.编排连
chain = {"query": RunnablePassthrough()}| prompt | llm | parser
# 5.调用连
resp = chain.stream("你好，你是谁？", config={"callbacks":[StdOutCallbackHandler(),LLMOpsCallbackHander()]})
for item in resp:
    pass