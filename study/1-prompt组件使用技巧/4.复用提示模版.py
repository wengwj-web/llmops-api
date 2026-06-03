#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/1 16:30
@Author : wwj
@File : 4.复用提示模版.py
"""
from langchain_core.prompts import PromptTemplate, PipelinePromptTemplate

full_template = PromptTemplate.from_template("""{introduction}

{example}

{start}""")

#描述模版
introduction_prompt = PromptTemplate.from_template("你正在模仿{person}")

#示例模版
example_prompt = PromptTemplate.from_template("""下面是一个交互例子：

Q:{example_q}
A:{example_a}""")

#开始模版
start_prompt = PromptTemplate.from_template("""根据用户的问题：
Q：{input}
A:""")

pipeline_prompts = [
    ("introduction", introduction_prompt),
    ("example", example_prompt),
    ("start", start_prompt),
]

pipeline_prompt = PipelinePromptTemplate(
    final_prompt=full_template,
    pipeline_prompts=pipeline_prompts,
)

print(pipeline_prompt.invoke({
    "person": "机器人",
    "example_q": "你能做什么？",
    "example_a": "编程",
    "input": "你是干嘛的？"
}).to_string())