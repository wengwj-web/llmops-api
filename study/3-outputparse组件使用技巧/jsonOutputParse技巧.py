#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time  : 2026/6/2 09:24
@Author : wwj
@File : jsonOutputParse技巧.py
"""
import dotenv
from langchain.chains.sql_database import query
from langchain_core.output_parsers import JsonOutputParser, format_instructions
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel,Field

dotenv.load_dotenv()

class Joke(BaseModel):
    joke: str = Field(description="回答用户冷笑话")
    punchline: str = Field(description="冷笑话的笑点")

parser = JsonOutputParser(pydantic_object=Joke)

#1.编排prompt
prompt = (ChatPromptTemplate.from_template("请根据用户提示进行回答：\n{format_instructions}\n{query}")
          .partial(format_instructions=parser.get_format_instructions()))
# print(prompt.format(query="请讲程序员冷笑话"))

#2.创建大语言模型
llm = ChatOpenAI(
    model="qwen2.5:1.5b",  # ✅ 具体的模型名
    openai_api_base="http://localhost:11434/v1",  # ✅ Ollama 的 OpenAI 兼容地址
    openai_api_key="ollama",  # ✅ 随便填，Ollama 不验证
    temperature=0.7
    # model="qwen2.5:1.5b",           # 或 qwen2.5:1.5b（如果内存不够）
    # base_url="http://localhost:11434",
    # temperature=0.7
)
#3. 输出解析器
content = parser.invoke(llm.invoke(prompt.invoke({"query":"请讲程序员冷笑话"})))
print(type(content))
print(content.get("punchline"))
print(content)