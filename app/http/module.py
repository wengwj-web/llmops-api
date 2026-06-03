#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/1 09:22
@Author : wwj
@File : module.py
"""
from flask_migrate import Migrate

from internal.extension.migrate_extension import migrate
from pkg.sqlalchemy import SQLAlchemy
from injector import Module, Binder

from internal.extension.database_extension import db


class ExtensionModule(Module):
    def configure(self, binder:Binder)->None:
        binder.bind(SQLAlchemy, to=db)
        binder.bind(Migrate, to=migrate)
