#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/3 23:45
@Author  : thezehui@gmail.com
@File    : 1.RAG多查询结果融合策略.py
"""

from typing import List

import dotenv
import weaviate
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.load import dumps, loads
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import Auth

dotenv.load_dotenv()


# 自定义多查询检索器（替代 MultiQueryRetriever）
class MultiQueryRetriever:
    """自定义多查询检索器基类"""

    def __init__(self, retriever, llm, prompt=None):
        self.retriever = retriever
        self.llm = llm
        self.prompt = prompt or ChatPromptTemplate.from_template(
            """请为以下查询生成3个不同的搜索变体：
原始查询：{question}

请输出3个查询，每行一个，不要编号："""
        )

    def generate_queries(self, question):
        response = self.llm.invoke(self.prompt.format(question=question))
        queries = [q.strip() for q in response.strip().split("\n") if q.strip()]
        return [question] + queries[:3]

    def retrieve(self, question):
        queries = self.generate_queries(question)
        seen = set()
        results = []
        for q in queries:
            docs = self.retriever.invoke(q)
            for doc in docs:
                key = doc.page_content[:100]
                if key not in seen:
                    seen.add(key)
                    results.append(doc)
        return results


class RAGFusionRetriever(MultiQueryRetriever):
    """RAG多查询结果融合策略检索器"""

    k: int = 4

    def retrieve_documents(
        self, queries: List[str], run_manager: CallbackManagerForRetrieverRun
    ) -> List[List]:
        """重写检索文档函数，返回值变成一个嵌套的列表"""
        documents = []
        for query in queries:
            docs = self.retriever.invoke(
                query, config={"callbacks": run_manager.get_child()}
            )
            documents.append(docs)
        return documents

    def unique_union(self, documents: List[List]) -> List[Document]:
        """使用RRF算法来去重合并对应的文档，参数为嵌套列表，返回值为文档列表"""
        # 1.定义一个变量存储每个文档的得分信息
        fused_result = {}

        # 2.循环两层获取每一个文档信息
        for docs in documents:
            for rank, doc in enumerate(docs):
                # 3.使用dumps函数将类示例转换成字符串
                doc_str = dumps(doc)
                # 4.判断下该文档的字符串是否已经计算过得分
                if doc_str not in fused_result:
                    fused_result[doc_str] = 0
                # 5.计算新的分
                fused_result[doc_str] += 1 / (rank + 60)

        # 6.执行排序操作，获取相应的数据，使用的是降序
        reranked_results = [
            (loads(doc), score)
            for doc, score in sorted(
                fused_result.items(), key=lambda x: x[1], reverse=True
            )
        ]

        return [item[0] for item in reranked_results[: self.k]]


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

rag_fusion_retriever = RAGFusionRetriever.from_llm(
    retriever=retriever,
    llm=ChatOpenAI(
        model="qwen2.5:1.5b",
        openai_api_base="http://localhost:11434/v1",
        openai_api_key="ollama",
        temperature=0.7,
    ),
)

# 3.执行检索
docs = rag_fusion_retriever.invoke("关于LLMOps应用配置的文档有哪些")
print(docs)
print(len(docs))
