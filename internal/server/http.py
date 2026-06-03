#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/5/28 17:06
@Author : wwj
@File : http.py
"""
import os
from logging import debug

from flask import Flask
from flask_migrate import Migrate

from config import Config
from internal.exception import CustomException
from internal.router import Router
from pkg.response import json, Response, HttpCode
from pkg.sqlalchemy import SQLAlchemy


class Http(Flask):
    """http服务引擎"""

    def __init__(self, *args, conf:Config, db:SQLAlchemy, migrate:Migrate, router:Router, **kwargs):
        # 1.调用父类函数初始化
        super().__init__(*args,**kwargs)

        # 2.初始化应用配置
        self.config.from_object(conf)

        # 3.注册绑定异常错误处理
        self.register_error_handler(Exception, self._register_error_handler)

        # 4.初始化数据库
        db.init_app(self)
        migrate.init_app(self, db, directory="internal/migration")
        # with self.app_context():
        #     _ = App()
        #     db.create_all()
        # 5.注册应用路由
        router.register_router(self)

    def _register_error_handler(self, error: Exception):
        if isinstance(error, CustomException):
            return json(Response(
                code=error.code,
                message=error.message,
                data=error.data if error.data else {},
            ))
        if debug or os.getenv("FLASK_ENV") == "development":
            raise error
        else:
            return json(Response(
                code= HttpCode.FAIL,
                message= str(error),
                data= {}
            ))

