#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/5/28 17:09
@Author : wwj
@File : app_service.py
"""

import dotenv
from flask_migrate import Migrate

from pkg.sqlalchemy import SQLAlchemy
from injector import Injector

from .module import ExtensionModule
from config import Config
from internal.router import Router
from internal.server import Http

#将env文件加载到变量中
dotenv.load_dotenv()

conf = Config()

injector = Injector([ExtensionModule])

app = Http(__name__, conf=conf,db=injector.get(SQLAlchemy), migrate=injector.get(Migrate), router=injector.get(Router))
app.config['SECRET_KEY'] = "2ef7c6e2b6ab1d235989c2cb9096508b2a908ef9318456500ffe167e7a3e7acb"

if __name__ == "__main__":
    app.run(debug=True)