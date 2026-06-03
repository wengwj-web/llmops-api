#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/1 13:36
@Author : wwj
@File : sqlalchemy.py
"""
from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy

class SQLAlchemy(_SQLAlchemy):
    """重写SQLAlchemy中的核心类 自动提交"""
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
