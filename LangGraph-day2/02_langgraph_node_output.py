# 此脚本展示错误的返回模式：直接返回一个state的后果
import operator
from typing import Annotated, List, TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph


class MyState(TypedDict):
    str_data:str
    add_list_data:Annotated[List[str],operator.add]
    add_str_data:Annotated[str,operator.add]

def node_1(state:MyState):
    print(state)
    str_data = state['str_data']
    state['str_data'] = "node_1"
    state['add_list_data'] = ["1"]
    # state['add_str_data'] = "1"
    return state

def node_2(state:MyState):
    print(state)
    str_data = state['str_data']
    state['str_data'] = "node_2"
    # state['add_list_data'] = ["2"]
    return state

def node_3(state:MyState):
    print(state)
    str_data = state['str_data']
    state['str_data'] = "node_3"
    # state['add_list_data'] = ["3"]
    return state

builder = StateGraph(MyState)
builder.add_node(node_1)
builder.add_node(node_2)
builder.add_node(node_3)
builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")
builder.add_edge("node_2","node_3")

graph = builder.compile()
result = graph.invoke({"str_data":"你好","add_list_data":["0"],"add_str_data":"1"})
print( result)