#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/5/29 16:43
@Author : wwj
@File : test_app_handler.py
"""
import pytest

from pkg.response import HttpCode

class TestAppHandler:
    """APP控制器测试类"""

    @pytest.mark.parametrize("query", [None, "你好，你是?"])
    def test_completion(self,query, client):
        resp= client.post("/app/completion", json={"query": query})
        assert resp.status_code == 200
        if query is None:
            assert resp.json.get("code") == HttpCode.VALIDATION_ERROR
        else:
            assert resp.json.get("code") == HttpCode.SUCCESS
        print("响应内容：",resp.json)
