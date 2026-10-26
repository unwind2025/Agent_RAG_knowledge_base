# 此脚本功能是展示条件边如何配置
# 条件边的执行逻辑：通过定义一个函数，从状态中取值，判断
from typing import TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph


class MyState(TypedDict):
    value: int


def input_node(state: MyState):
    print("开始获取输入数据....")
    return {"value": 10086}


def odd_node(state: MyState):
    value = state["value"]
    print(f"{value}是奇数！")


def even_node(state: MyState):
    value = state["value"]
    print(f"{value}是偶数！")


def route_condition(state: MyState):
    value = state["value"]
    if value % 2 == 0:
        return "even"
    else:
        return "odd"


builder = StateGraph(MyState)
builder.add_node(input_node)
builder.add_node(odd_node)
builder.add_node(even_node)
builder.add_edge(START, "input_node")
builder.add_conditional_edges(
    "input_node",  # 起始节点的映射名
    route_condition,  # 路由函数
    {
        "even": "even_node",
        "odd": "odd_node"
    }
)
graph = builder.compile()
graph.invoke({})
