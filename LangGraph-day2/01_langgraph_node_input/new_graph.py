from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from new_config import config
from new_runtime import Atguigu
from langgraph.constants import START
from langgraph.graph import StateGraph


class MyState(TypedDict):
    query: str
    response: str





def node_1(state:MyState,config:RunnableConfig):
    configurable = config.get("configurable",{})
    user_id = configurable.get("user_id","downguigu")
    print(user_id)

def node_2(state:MyState,runtime:Runtime):
    atguigu = runtime.context["sgg"]
    atguigu.show()

builder = StateGraph(state_schema=MyState)

builder.add_node(node_1)
builder.add_node(node_2)
builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")

graph = builder.compile()
my_atguigu = Atguigu()
context = {
    "sgg":my_atguigu
}

result = graph.invoke({"query":"哈喽"},config=config,context=context)



