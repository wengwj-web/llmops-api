#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/5/29 16:50
@Author : wwj
@File : conftest.py
"""
import pytest
from app.http.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client