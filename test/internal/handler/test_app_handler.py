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

    @pytest.mark.parametrize(
        "app_id, query",
        [
            ("72c738f2-2de3-4776-bc19-fcac930ccfb1", None),
            ("72c738f2-2de3-4776-bc19-fcac930ccfb1", "你好，你是？"),
        ],
    )
    def test_completion(self, app_id, query, client):
        resp = client.post(f"/apps/{app_id}/debug", json={"query": query})
        assert resp.status_code == 200
        if query is None:
            assert resp.json.get("code") == HttpCode.VALIDATION_ERROR
        else:
            assert resp.json.get("code") == HttpCode.SUCCESS
        print("响应内容：", resp.json)
