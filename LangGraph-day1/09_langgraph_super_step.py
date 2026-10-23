# 此脚本通过构建一个较为复杂的例子，展示LangGraph底层运行的原理
import operator
from typing import TypedDict, Annotated, List

from langgraph.constants import START
from langgraph.graph import StateGraph


class MyState(TypedDict):
    data_list:Annotated[List[str],operator.add]

def a(state:MyState):
    return {"data_list":["a"]}
def b_1(state:MyState):
    return {"data_list":["b_1"]}
def b_2(state:MyState):
    return {"data_list":["b_2"]}
def c(state:MyState):
    return {"data_list":["c"]}
def d(state:MyState):
    return {"data_list":["d"]}

builder = StateGraph(MyState)
builder.add_node(a)
builder.add_node(b_1)
builder.add_node(b_2)
builder.add_node(c)
builder.add_node(d)

builder.add_edge(START,"a")
builder.add_edge("a","b_1")
builder.add_edge("b_1","b_2")
builder.add_edge("a","c")
builder.add_edge("c","d")
builder.add_edge("b_2","d")

graph = builder.compile()
result = graph.invoke({})
print(result)

# A :[a,b_1,b_2,c,d]
# B :[a,c,b_1,b_2,d]
# C :[a,b_1,c,b_2,d]
# D :我觉得都不对，我的答案是：[]