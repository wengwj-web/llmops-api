#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/8/25 14:22
@Author  : thezehui@gmail.com
@File    : dataset_handler.py
"""

from dataclasses import dataclass
from uuid import UUID

from flask import request
from injector import inject

from internal.code.file_extractor import FileExtractor
from internal.model import UploadFile
from internal.schema.dataset_schema import (
    CreateDatasetReq,
    GetDatasetResp,
    UpdateDatasetReq,
    GetDatasetsWithPageReq,
    GetDatasetsWithPageResp,
    GetDatasetQueriesResp,
    HitReq,
)
from internal.service import (
    DatasetService,
    JiebaService,
    EmbeddingsService,
    VectorDatabaseService,
)
from pkg.paginator import PageModel
from pkg.response import validate_error_json, success_message, success_json
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class DatasetHandler:
    """知识库处理器"""

    db: SQLAlchemy
    dataset_service: DatasetService
    embeddings_service: EmbeddingsService
    jieba_service: JiebaService
    file_extractor: FileExtractor
    vector_database_service: VectorDatabaseService

    def embeddings_query(self):
        upload_file = self.db.session.query(UploadFile).get(
            "3f1d5352-a1a4-4461-88ea-95a6f306c8c1"
        )
        content = self.file_extractor.load(upload_file, True)
        return success_json({"content": content})
        # query = request.args.get("query")
        # keywords = self.jieba_service.extract_keywords(query)
        # return success_json({"keywords": keywords})
        # vectors = self.embeddings_service.embeddings.embed_query(query)
        # return success_json({"keywords": vectors})

    def hit(self, dataset_id: UUID):
        """根据传递的知识库id+检索参数执行召回测试"""
        # # 1.提取数据并校验
        # req = HitReq()
        # if not req.validate():
        #     return validate_error_json(req.errors)
        #
        # # 2.调用服务执行检索策略
        # hit_result = self.dataset_service.hit(dataset_id, req)
        #
        # return success_json(hit_result)
        from weaviate.classes.query import Filter

        query = "删除知识库"
        retriever = self.vector_database_service.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 10,
                "filter": Filter.all_of(
                    [
                        Filter.by_property("document_enabled").equal(True),
                        Filter.by_property("segment_enabled").equal(True),
                        Filter.any_of(
                            [
                                Filter.by_property("dataset_id").equal(
                                    "c1606cd6-3f74-46fe-b62e-567f4f868b1e"
                                ),
                                Filter.by_property("dataset_id").equal(
                                    "c1606cd6-3f74-46fe-b62e-567f4f868b2e"
                                ),
                            ]
                        ),
                    ]
                ),
            },
        )

        documents = retriever.invoke(query)
        return success_json(
            {
                "documents": [
                    {
                        "page_content": document.page_content,
                        "metadata": document.metadata,
                    }
                    for document in documents
                ]
            }
        )

    def get_dataset_queries(self, dataset_id: UUID):
        """根据传递的知识库id获取最近的10条查询记录"""
        dataset_queries = self.dataset_service.get_dataset_queries(dataset_id)
        resp = GetDatasetQueriesResp(many=True)
        return success_json(resp.dump(dataset_queries))

    def create_dataset(self):
        """创建知识库"""
        # 1.提取请求并校验
        req = CreateDatasetReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务创建知识库
        self.dataset_service.create_dataset(req)

        # 3.返回成功调用提示
        return success_message("创建知识库成功")

    def get_dataset(self, dataset_id: UUID):
        """根据传递的知识库id获取详情"""
        dataset = self.dataset_service.get_dataset(dataset_id)
        resp = GetDatasetResp()

        return success_json(resp.dump(dataset))

    def update_dataset(self, dataset_id: UUID):
        """根据传递的知识库id+信息更新知识库"""
        # 1.提取请求并校验
        req = UpdateDatasetReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务创建知识库
        self.dataset_service.update_dataset(dataset_id, req)

        # 3.返回成功调用提示
        return success_message("更新知识库成功")

    def get_datasets_with_page(self):
        """获取知识库分页+搜索列表数据"""
        # 1.提取query数据并校验
        req = GetDatasetsWithPageReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.调用服务获取分页数据
        datasets, paginator = self.dataset_service.get_datasets_with_page(req)

        # 3.构建响应
        resp = GetDatasetsWithPageResp(many=True)

        return success_json(PageModel(list=resp.dump(datasets), paginator=paginator))
