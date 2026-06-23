#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/5 0:52
@Author  : thezehui@gmail.com
@File    : 1.混合策略实现doc-doc对称检索.py
"""

from typing import List

import dotenv
import weaviate
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey, Auth

dotenv.load_dotenv()


class HyDERetriever(BaseRetriever):
    """HyDE混合策略检索器"""

    retriever: BaseRetriever
    llm: BaseLanguageModel

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """传递检索query实现HyDE混合策略检索"""
        # 1.构建生成假设性文档的prompt
        prompt = ChatPromptTemplate.from_template(
            "请写一篇科学论文来回答这个问题。\n" "问题: {question}\n" "文章: "
        )

        # 2.构建HyDE混合策略检索链
        chain = (
                {"question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
                | self.retriever
        )

        return chain.invoke(query)


# 1.构建向量数据库与检索器
db = WeaviateVectorStore(
    client=weaviate.connect_to_weaviate_cloud(
        cluster_url="j9llgsobrtqlna9jjsppa.c0.eu-central-1.aws.weaviate.cloud",
        auth_credentials=Auth.api_key(
            "Y0djTW5FSzRWYmwwc1MxOV9Icy9VdjNiZWcxUzJ1ZUpvUU5RdG5XR1JiQnlYY085Q08xV1oybG9MaGRNPV92MjAw"
        ),
    ),
    index_name="DatasetDemo",
    text_key="text",
    embedding=OllamaEmbeddings(
        model="nomic-embed-text", base_url="http://localhost:11434"
    ),
)
retriever = db.as_retriever(search_type="mmr")

# 2.创建HyDE检索器
hyde_retriever = HyDERetriever(
    retriever=retriever,
    llm=ChatOpenAI(
        model="qwen2.5:1.5b",
        temperature=0.7,
    ),
)

# 3.检索文档
documents = hyde_retriever.invoke("关于LLMOps应用配置的文档有哪些？")
print(documents)
print(len(documents))
