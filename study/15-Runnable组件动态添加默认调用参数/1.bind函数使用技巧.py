from multiprocessing.resource_sharer import stop

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "你正在执行一项测试，请重复用户传递的内容，除了重复其他均不要操作"),
    ("human", "{query}")
])

llm = ChatOpenAI(
    model="qwen2.5:1.5b",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    temperature=0.7,
)

chain = prompt | llm.bind(stop="world") | StrOutputParser()

content = chain.invoke({"query": "hello world"})
print(content)