#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/5/23 1:55
@Author  : thezehui@gmail.com
@File    : conversation_buffer_window_memory.py
"""
from typing import Dict, List, Any

from langchain_community.chat_message_histories import FileChatMessageHistory


class ConversationBufferWindowMemory:
    """缓冲窗口记忆：保留最近 k 轮对话"""

    def __init__(
        self,
        k: int = 3,
        input_key: str = "query",
        output_key: str = "output",
        return_messages: bool = True,
        chat_memory: FileChatMessageHistory = None
    ):
        self.k = k
        self.input_key = input_key
        self.output_key = output_key
        self.return_messages = return_messages
        self.chat_memory = chat_memory

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """加载记忆变量，只返回最近 k 轮对话"""
        all_messages = self.chat_memory.messages
        keep_count = self.k * 2
        recent_messages = all_messages[-keep_count:] if len(all_messages) > keep_count else all_messages

        return {"history": recent_messages}  # ✅ 返回 BaseMessage 列表

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """保存对话上下文"""
        query = inputs.get(self.input_key, "")
        output = outputs.get(self.output_key, "")

        self.chat_memory.add_user_message(query)
        self.chat_memory.add_ai_message(output)

    def clear(self) -> None:
        """清空记忆"""
        self.chat_memory.clear()