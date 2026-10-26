# 这个脚本用于展示LangGraph中的循环操作
import operator
from typing import TypedDict, Annotated

from langgraph.constants import START, END
from langgraph.graph import StateGraph


class MyState(TypedDict):
    value: Annotated[int, operator.add]


def node_1(state: MyState):
    value = state["value"]
    print(f"当前值为：{value}")
    return {"value": 1}


def node_2(state: MyState):
    value = state["value"]
    print(f"当前值为：{value}")
    return {"value": 1}


def route_condition(state: MyState):
    value = state["value"]
    if value < 30:
        return "node_1"
    else:
        return "end"


builder = StateGraph(MyState)
builder.add_node(node_1)
builder.add_node(node_2)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_conditional_edges(
    "node_2",
    route_condition,
    {
        "node_1": "node_1",
        "end": END
    }
)
graph = builder.compile()
graph.invoke({"value": 1}, config={
    'recursion_limit': 100  # 设置递归限制
    }
)
