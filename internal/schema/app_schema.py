#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/5/29 14:41
@Author : wwj
@File : app_schema.py
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, length


class CompletionReq(FlaskForm):
    """基础聊天接口请求验证"""
    query = StringField("query", validators=[
        DataRequired(message="用户的提问是必填的"),
        length(max=2000, message="用户提问的最大长度是2000")
    ])
