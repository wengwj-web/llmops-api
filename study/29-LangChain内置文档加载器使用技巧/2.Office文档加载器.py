#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/1 18:46
@Author  : thezehui@gmail.com
@File    : 2.Office文档加载器.py
"""

from langchain_community.document_loaders import (
    UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
)

# excel_loader = UnstructuredExcelLoader("./员工考勤表.xlsx", mode="elements")
# excel_documents = excel_loader.load()
#
# print(excel_documents)
# print(len(excel_documents))
# print(excel_documents[0].metadata)

# word_loader = UnstructuredWordDocumentLoader("./喵喵.docx")
# documents = word_loader.load()
# print(documents)
# print(len(documents))
# print(documents[0].metadata)

ppt_loader = UnstructuredPowerPointLoader("./章节介绍.pptx")
documents = ppt_loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
