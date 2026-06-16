#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/17 9:18
@Author  : thezehui@gmail.com
@File    : 3.Pinecone删除数据.py
"""

import dotenv
from langchain_community.embeddings import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore

dotenv.load_dotenv()

embedding = OllamaEmbeddings(
    model="nomic-embed-text", base_url="http://localhost:11434"
)
db = PineconeVectorStore(index_name="llmops", embedding=embedding, namespace="dataset")

id = "6946d264-253b-47d3-a2b1-f74baa82a2d1"
db.delete([id], namespace="dataset")
# pinecone_index = db.get_pinecone_index("llmops")
# pinecone_index.update(id="xxx", values=[], metadata={}, namespace="xxx")
