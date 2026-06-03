#!/usr/bin/venv python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/5/28 16:09
@Author : wwj
@File : test.py
"""
from injector import Injector, inject

class A:
    name:str = "llmops"

@inject
class B:
    def __init__(self,a:A):
        self.a = a

    def print(self):
        print(f"class A的name:{self.a.name}")

injector = Injector()
b = injector.get(B)
b.print()