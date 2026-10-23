# 此案例目的是展示如何在节点的参数里进行多种数据的注入
# 比如说：状态，配置参数，类对象
from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

from config import config
from runtime import Atguigu

class MyState(TypedDict):
    query:str
    response:str

def node_1(state:MyState,config:RunnableConfig):
    configurable = config.get("configurable",{})
    user_id = configurable.get("user_id","downguigu")
    print(user_id)

def node_2(state:MyState,runtime:Runtime):
    atguigu = runtime.context['sgg']
    atguigu.show()

builder = StateGraph(state_schema=MyState)
builder.add_node(node_1)
builder.add_node(node_2)
builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")
builder.add_edge("node_2",END)

graph = builder.compile()
my_atguigu = Atguigu()
context = {
    "sgg":my_atguigu
}

result = graph.invoke({"query":"哈喽"},config = config,context =context)