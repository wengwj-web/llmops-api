#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/1 10:09
@Author : wwj
@File : app_service.py
"""

import uuid

from pkg.sqlalchemy import SQLAlchemy
from injector import inject
from dataclasses import dataclass

from internal.model import App, Account


@inject
@dataclass
class AppService:
    db: SQLAlchemy

    def create_app(self, account: Account) -> App:
        with self.db.auto_commit():
            app = App(
                name="测试机器人",
                account_id=account.id,
                icon="",
                description="这是一个简单的聊天机器人",
            )
            self.db.session.add(app)
        # self.db.session.commit()
        return app

    def get_app(self, id: uuid.UUID) -> App:
        return self.db.session.query(App).get(id)

    def update_app(self, id: uuid.UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            app.name = "我的机器人"
        # self.db.session.commit()
        return app

    def delete_app(self, id: uuid.UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            self.db.session.delete(app)
        # self.db.session.commit()
        return app
