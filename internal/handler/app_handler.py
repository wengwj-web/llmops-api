#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/5/28 16:37
@Author : wwj
@File : app_handler.py
"""

import json
import uuid
from dataclasses import dataclass
from operator import itemgetter
from typing import Any, Dict, Literal, Generator
from threading import Thread
from uuid import UUID
from queue import Queue
from injector import inject
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.messages import ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig
from langchain_core.tracers import Run
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph
from langgraph.constants import END

from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import (
    success_json,
    validate_error_json,
    success_message,
    compact_generate_response,
)
from internal.code.tools.builtin_tools.providers import BuiltinProviderManager
from internal.service import (
    AppService,
    VectorDatabaseService,
    ApiToolService,
    EmbeddingsService,
    ConversationService,
)
from internal.task.demo_task import demo_task


@inject
@dataclass
class AppHandler:
    """应用控制器"""

    app_service: AppService
    api_tool_service: ApiToolService
    embeddings_service: EmbeddingsService
    builtin_provider_manager: BuiltinProviderManager
    vector_database_service: VectorDatabaseService
    conversation_service: ConversationService

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

    def debug(self, app_id: UUID):
        """应用会话调试聊天接口，该接口为流式事件输出"""
        # 1.提取从接口中获取的输入，POST
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.创建队列并提取query数据
        q = Queue()
        query = req.query.data

        # 3.创建graph图程序应用
        def graph_app() -> None:
            """创建Graph图程序应用并执行"""
            # 3.1 创建tools工具列表
            tools = [
                self.builtin_provider_manager.get_tool("google", "google_serper")(),
                self.builtin_provider_manager.get_tool("gaode", "gaode_weather")(),
                self.builtin_provider_manager.get_tool("dalle", "dalle3")(),
            ]

            # 3.2 定义大语言模型/聊天机器人节点
            def chatbot(state: MessagesState) -> MessagesState:
                """聊天机器人节点"""
                # 3.2.1 创建LLM大语言模型
                llm = ChatOpenAI(model="qwen2.5:1.5b", temperature=0.7).bind_tools(
                    tools
                )

                # 3.2.2 调用stream()函数获取流式输出内容，并判断生成内容是文本还是工具调用参数
                is_first_chunk = True
                is_tool_call = False
                gathered = None
                id = str(uuid.uuid4())
                for chunk in llm.stream(state["messages"]):
                    # 3.2.3 检测是不是第一个块，部分LLM的第一个块不会生成内容，需要抛弃掉
                    if is_first_chunk and chunk.content == "" and not chunk.tool_calls:
                        continue

                    # 3.2.4 叠加相应的区块
                    if is_first_chunk:
                        gathered = chunk
                        is_first_chunk = False
                    else:
                        gathered += chunk

                    # 3.2.5 判断是工具调用还是文本生成，往队列中添加不同的数据
                    if chunk.tool_calls or is_tool_call:
                        is_tool_call = True
                        q.put(
                            {
                                "id": id,
                                "event": "agent_thought",
                                "data": json.dumps(chunk.tool_call_chunks),
                            }
                        )
                    else:
                        q.put(
                            {
                                "id": id,
                                "event": "agent_message",
                                "data": chunk.content,
                            }
                        )

                return {"messages": [gathered]}

            # 3.3 定义工具/函数调用节点
            def tool_executor(state: MessagesState) -> MessagesState:
                """工具执行节点"""
                # 3.3.1 提取数据状态中的tool_calls
                tool_calls = state["messages"][-1].tool_calls

                # 3.3.2 将工具列表转换成字典便于使用
                tools_by_name = {tool.name: tool for tool in tools}

                # 3.3.3 执行工具并得到对应的结果
                messages = []
                for tool_call in tool_calls:
                    id = str(uuid.uuid4())
                    tool = tools_by_name[tool_call["name"]]
                    tool_result = tool.invoke(tool_call["args"])
                    messages.append(
                        ToolMessage(
                            tool_call_id=tool_call["id"],
                            content=json.dumps(tool_result),
                            name=tool_call["name"],
                        )
                    )
                    q.put(
                        {
                            "id": id,
                            "event": "agent_action",
                            "data": json.dumps(tool_result),
                        }
                    )

                return {"messages": messages}

            # 3.4 定义路由函数
            def route(state: MessagesState) -> Literal["tool_executor", "__end__"]:
                """定义路由节点，用于确认下一步步骤"""
                ai_message = state["messages"][-1]
                if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
                    return "tool_executor"
                return END

            # 3.5 创建状态图
            graph_builder = StateGraph(MessagesState)

            # 3.6 添加节点
            graph_builder.add_node("llm", chatbot)
            graph_builder.add_node("tool_executor", tool_executor)

            # 3.7 添加边
            graph_builder.set_entry_point("llm")
            graph_builder.add_conditional_edges("llm", route)
            graph_builder.add_edge("tool_executor", "llm")

            # 3.8 编译图程序为可运行组件
            graph = graph_builder.compile()

            # 3.9 调用图结构程序并获取结果
            result = graph.invoke({"messages": [("human", query)]})
            print("最终结果: ", result)
            q.put(None)

        def stream_event_response() -> Generator:
            """流式事件输出响应"""
            # 1.从队列中获取数据并使用yield抛出
            while True:
                item = q.get()
                if item is None:
                    break
                # 2.使用yield关键字返回对应的数据
                yield f"event: {item.get('event')}\ndata: {json.dumps(item)}\n\n"
                q.task_done()

        t = Thread(target=graph_app)
        t.start()

        return compact_generate_response(stream_event_response())

    def _debug(self, app_id: uuid.UUID):
        """聊天接口"""

        # 1. 提取从接口中获取的输入，post
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

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

        llm = ChatOpenAI(model="qwen2.5:1.5b", temperature=0.7)
        retriever = (
            self.vector_database_service.get_retriever()
            | self.vector_database_service.combine_documents
        )
        chain = (
            RunnablePassthrough.assign(
                history=RunnableLambda(self._load_memory_variables)
                | itemgetter("history"),
                context=itemgetter("query") | retriever,
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
        from internal.code.agent.agents import FunctionCallAgent
        from internal.code.agent.entities.agent_entity import AgentConfig
        from langchain_openai import ChatOpenAI

        agent = FunctionCallAgent(
            AgentConfig(
                llm=ChatOpenAI(model="glm-4-flash"),
                preset_prompt="你是一个拥有20年经验的诗人，请根据用户提供的主题来写一首诗",
            )
        )
        state = agent.run("程序员", [], "")
        content = state["messages"][-1].content
        return success_json({"content": content})

        # human_message = "你能简单介绍下LLM吗？你知道LLM与Agent的区别"
        # ai_message = """你好，我是千问，有什么可以帮到你的？"""
        # old_summary = """人类询问AI关于LLM与Agent的概念。AI解释了它们之间的区别，并详细介绍了LLM和Agent的主要功能。\n\n当前总结:\n人类询问AI对人工智能的看法，AI认为人工智能是一股向善的力量，因为它将帮助人类发挥全部潜力。\n\n新的会话:\nHuman: 你能简单介绍下什么是LLM与Agent吗？\nAI: \n        LLM 是“会说话的大脑”，负责思考与生成。有问必答，但只能“口嗨”，无法主动调用外部系统或帮你做事（如 GPT-4、Claude）。\n\nAgent（智能体）：以 LLM 为核心，具备感知、规划、记忆和工具调用能力。给它一个目标，它能自己查资料、跑代码、发邮件并自动完成任务（如你项目中用 LangGraph 编排的系统）。\n        \n\n新的总结:\n人类询问AI对人工智能的看法，AI认为人工智能是一股向善的力量，因为它将帮助人类发挥全部潜力。接着解释了LLM和Agent的概念：LLM负责思考与生成，有问必答但无法主动调用外部系统；而Agent则具备感知、规划、记忆和工具调用能力，能自主完成任务。"""
        # summary = self.conversation_service.summary(
        #     human_message, ai_message, old_summary
        # )
        # conversation_name = self.conversation_service.generate_conversation_name(
        #     human_message
        # )
        # questions = self.conversation_service.generate_suggested_questions(
        #     human_message
        # )
        # return success_json({"questions": questions})
        # demo_task.delay(uuid.uuid4())
        # return self.api_tool_service.api_tool_invoke()
        # raise FailException("数据未找到异常")
        # return {"ping": "pong"}
