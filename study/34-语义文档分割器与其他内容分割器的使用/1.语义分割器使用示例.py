#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/2 14:33
@Author  : thezehui@gmail.com
@File    : 1.语义分割器使用示例.py
"""

import dotenv
import os
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.document_transformers import DoctranQATransformer
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings

# 劫持 OpenAI 客户端指向 Ollama
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"

dotenv.load_dotenv()

documents = [Document(page_content="你的文档内容...")]

# 用对话模型，不要用嵌入模型
loader = DoctranQATransformer(
    openai_api_key="ollama",
    openai_model="qwen2.5:1.5b",  # 或 llama3 等对话模型
    openai_deployment_id="qwen2.5:1.5b",
)

# 2.加载文本与分割
documents = loader.load()
chunks = text_splitter.split_documents(documents)

# 3.循环打印
for chunk in chunks:
    print(f"块大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")
