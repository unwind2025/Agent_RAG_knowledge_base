# 此脚本展示使用LangGraph中的“中断”操作
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class MyState(TypedDict):
    user_input:str
    result:str

def node_1(state:MyState):
    user_input = state['user_input']
    print(f"获取了用户的输入：{user_input}")

    extra_input = interrupt(
        {"node":"node_1",
         "description":"现在需要用户提供一些额外的补充信息",
         "date":"2026/7/4"}
    )

    print(extra_input)
    # return {"result":extra_input}

builder = StateGraph(MyState)
builder.add_node(node_1)
builder.add_edge(START,"node_1")
checkpointer = InMemorySaver()
config = {"configurable":{"thread_id":"id_1"}}
graph = builder.compile(checkpointer = checkpointer)
response = graph.invoke({"user_input":"哈哈"},config = config)
print(response)
response = graph.invoke(Command(resume ={"permit":"允许"}),config = config)
