#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/1 09:22
@Author : wwj
@File : module.py
"""

from flask_migrate import Migrate

from internal.extension import redis_extension
from internal.extension.migrate_extension import migrate
from pkg.sqlalchemy import SQLAlchemy
from injector import Module, Binder, Injector
from internal.extension.redis_extension import redis_client
from internal.extension.database_extension import db
from redis import Redis
from flask_login import LoginManager
from internal.extension.login_extension import login_manager


class ExtensionModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(SQLAlchemy, to=db)
        binder.bind(Migrate, to=migrate)
        binder.bind(Redis, to=redis_client)
        binder.bind(LoginManager, to=login_manager)


injector = Injector([ExtensionModule])
