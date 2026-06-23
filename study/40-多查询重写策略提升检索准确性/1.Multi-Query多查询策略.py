#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/3 9:25
@Author  : thezehui@gmail.com
@File    : 1.Multi-Query多查询策略.py
"""

import dotenv
import weaviate
from langchain.retrievers import MultiQueryRetriever
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import Auth

dotenv.load_dotenv()

# 1.构建向量数据库与检索器
db = WeaviateVectorStore(
    client=weaviate.connect_to_weaviate_cloud(
        cluster_url="3a4mbufdsxmjgrver7tdlw.c0.eu-central-1.aws.weaviate.cloud",
        auth_credentials=Auth.api_key(
            "anVnNkhXUTUyMEg3M0l3OF9QRHAvZU9qeXVBN2ZrT1pvYlRwUWtwd01vYzI2UHlIcitUNFpZaG1QZFZzPV92MjAw"
        ),
    ),
    index_name="DatasetDemo",
    text_key="text",
    embedding=OllamaEmbeddings(
        model="nomic-embed-text", base_url="http://localhost:11434"
    ),
)
retriever = db.as_retriever(search_type="mmr")

# 2.创建多查询检索器
multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=ChatOpenAI(
        model="qwen2.5:1.5b",
        openai_api_base="http://localhost:11434/v1",
        openai_api_key="ollama",
        temperature=0.7,
    ),
    include_original=True,
)

# 3.执行检索
docs = multi_query_retriever.invoke("关于LLMOps应用配置的文档有哪些")
print(docs)
print(len(docs))
