#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/30 16:34
@Author  : thezehui@gmail.com
@File    : vector_database_service.py
"""

import atexit
import os

import weaviate
from injector import inject
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_weaviate import WeaviateVectorStore
from weaviate import WeaviateClient
from weaviate.collections import Collection

from .embeddings_service import EmbeddingsService

# 向量数据库的集合名字
COLLECTION_NAME = "Dataset"

# 全局单例，避免重复创建连接
_weaviate_client: WeaviateClient | None = None
_vector_store: WeaviateVectorStore | None = None


def _close_weaviate():
    """程序退出时关闭 Weaviate 连接"""
    global _weaviate_client
    if _weaviate_client is not None:
        _weaviate_client.close()
        _weaviate_client = None
        print("Weaviate connection closed.")


# 注册退出钩子
atexit.register(_close_weaviate)


@inject
class VectorDatabaseService:
    """向量数据库服务"""

    client: WeaviateClient
    vector_store: WeaviateVectorStore
    embeddings_service: EmbeddingsService

    def __init__(self, embeddings_services: EmbeddingsService):
        # """构造函数，完成向量数据库服务的客户端+LangChain向量数据库实例的创建"""
        #
        # # 1.赋值embeddings_service
        # self.embeddings_service = embeddings_services
        #
        # # 2.创建/连接weaviate向量数据库
        # self.client = weaviate.connect_to_local(
        #     host=os.getenv("WEAVIATE_HOST"), port=int(os.getenv("WEAVIATE_PORT"))
        # )
        #
        # # 3.创建LangChain向量数据库
        # self.vector_store = WeaviateVectorStore(
        #     client=self.client,
        #     index_name=COLLECTION_NAME,
        #     text_key="text",
        #     embedding=self.embeddings_service.cache_backed_embeddings,
        #     # embedding=self.embeddings_service.embeddings,
        # )
        """构造函数，复用全局 Weaviate 连接"""
        global _weaviate_client, _vector_store

        # 1. 赋值 embeddings_service
        self.embeddings_service = embeddings_services

        # 2. 复用或创建 weaviate 连接
        if _weaviate_client is None:
            _weaviate_client = weaviate.connect_to_local(
                host=os.getenv("WEAVIATE_HOST"), port=int(os.getenv("WEAVIATE_PORT"))
            )
        self.client = _weaviate_client

        # 3. 复用或创建 LangChain 向量数据库
        if _vector_store is None:
            _vector_store = WeaviateVectorStore(
                client=self.client,
                index_name=COLLECTION_NAME,
                text_key="text",
                embedding=self.embeddings_service.cache_backed_embeddings,
            )
        self.vector_store = _vector_store

    def get_retriever(self) -> VectorStoreRetriever:
        """获取检索器"""
        return self.vector_store.as_retriever()

    @classmethod
    def combine_documents(cls, documents: list[Document]) -> str:
        """将对应的文档列表使用换行符进行合并"""
        return "\n\n".join([document.page_content for document in documents])

    @property
    def collection(self) -> Collection:
        return self.client.collections.get(COLLECTION_NAME)
