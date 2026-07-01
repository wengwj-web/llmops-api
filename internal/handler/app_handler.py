#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/5/28 16:37
@Author : wwj
@File : app_handler.py
"""

import uuid
from dataclasses import dataclass
from operator import itemgetter
from typing import Dict, Any

from injector import inject
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig
from langchain_core.tracers import Run
from langchain_openai import ChatOpenAI

from internal.code.tools.builtin_tools.providers import BuiltinProviderManager
from internal.exception import FailException
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import success_json, validation_error_json, success_message
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_classic.schema import BaseMemory


@inject
@dataclass
class AppHandler:
    """应用控制器"""

    app_service: AppService

    def create_app(self):
        app = self.app_service.create_app()
        return success_message(f"应用已经创建成功, id={app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_message(f"应用已经成功获取, id={app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        return success_message(f"应用已经成功修改, id={app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"应用已经成功删除, id={app.id}")

    @classmethod
    def _load_memory_variables(
            cls, input: Dict[str, Any], config: RunnableConfig
    ) -> Dict[str, Any]:
        """加载记忆变量信息"""
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(
                configurable_memory, BaseMemory
        ):
            return configurable_memory.load_memory_variables(input)

        return {"history": []}

    @classmethod
    def _save_context(cls, run_obj: Run, config: RunnableConfig) -> None:
        """存储对应的上下文信息到记忆实体中"""
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(
                configurable_memory, BaseMemory
        ):
            configurable_memory.save_context(run_obj.inputs, run_obj.outputs)

    def debug(self, app_id: uuid.UUID):
        """聊天接口"""

        # 1. 提取从接口中获取的输入，post
        req = CompletionReq()
        if not req.validate():
            return validation_error_json(req.errors)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个强大的聊天机器人，能根据用户的提问回复对应的问题"),
                MessagesPlaceholder("history"),
                ("human", "{query}"),
            ]
        )

        memory = ConversationBufferWindowMemory(
            k=3,
            input_key="query",
            output_key="output",
            return_messages=True,
            chat_memory=FileChatMessageHistory("./storage/memory/chat_history.txt"),
        )

        llm = ChatOpenAI(
            model="qwen2.5:1.5b",
            openai_api_base="http://localhost:11434/v1",
            openai_api_key="ollama",
            temperature=0.7,
        )
        chain = (
                RunnablePassthrough.assign(
                    history=RunnableLambda(self._load_memory_variables)
                            | itemgetter("history"),
                )
                | prompt
                | llm
                | StrOutputParser()
        ).with_listeners(on_end=self._save_context)

        chain_input = {"query": req.query.data}
        content = chain.invoke(chain_input, config={"configurable": {"memory": memory}})
        # memory.save_context(chain_input,{"output":content})

        # # 2.构建组件
        # prompt = ChatPromptTemplate.from_template("{query}")
        # llm = ChatOpenAI(model="qwen2.5:1.5b", openai_api_base="http://localhost:11434/v1",openai_api_key="ollama",temperature=0.7)
        # parser = StrOutputParser()
        # # 3.构建连
        # chain = prompt | llm | parser
        #
        # # 4.调用连输出结果
        # content = chain.invoke({"query": req.query.data})
        # local
        # query = request.json.get("query")
        # client = OpenAI(base_url=os.getenv("OPENAI_API_BASE"))
        # completion = client.chat.completions.create(
        #     model="qwen2.5:1.5b",
        #     messages=[
        #         {"role": "system","content": "我是来自阿里云的语言模型，我叫通义千问。很高兴认识你！"},
        #         {"role": "user","content": query}
        #     ]
        # )
        # clude
        # client = OpenAI(base_url=os.getenv("OPENAI_API_BASE"))
        # completion = client.chat.completions.create(
        #     model="deepseek-v3-0324",
        #     messages=[
        #         {"role": "system","content": "我是来自阿里云的语言模型，我叫通义千问。很高兴认识你！"},
        #         {"role": "user","content": query}
        #     ]
        # )
        # content = completion.choices[0].message.content
        print(content)
        return success_json({"content": content})

    def ping(self):
        # raise FailException("数据未找到异常")
        return {"ping": "pong"}
