#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/7 19:28
@Author  : thezehui@gmail.com
@File    : 1.Cohere重排序示例.py
"""

import dotenv
import weaviate
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain_ollama import OllamaEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import Auth

dotenv.load_dotenv()

# 1.创建向量数据库与重排组件
embedding = OllamaEmbeddings(
    model="nomic-embed-text", base_url="http://localhost:11434"
)
db = WeaviateVectorStore(
    client=weaviate.connect_to_weaviate_cloud(
        cluster_url="jq8u4jgdr7ojtxennje8fq.c0.eu-central-1.aws.weaviate.cloud",
        auth_credentials=Auth.api_key(
            "REh2WUpNM091aEhSQkhwRV9uU3hJT1p2MFYzWlhsM3BrWUpnemxCbXRVMEVVaVZlb1d2eXhUajZUU0kwPV92MjAw"
        ),
    ),
    index_name="ParentDocument",
    text_key="text",
    embedding=embedding,
)
rerank = CohereRerank(model="rerank-multilingual-v3.0")

# 2.构建压缩检索器
retriever = ContextualCompressionRetriever(
    base_retriever=db.as_retriever(seaarch_type="mmr"),
    base_compressor=rerank,
)

# 3.执行搜索并排序
search_docs = retriever.invoke("关于LLMOps应用配置的信息有哪些呢？")
print(search_docs)
print(len(search_docs))
