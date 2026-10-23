# 此脚本用于展示LangGraph中状态的更新方式设置
import operator
from typing import TypedDict, Annotated, List

from langgraph.constants import START, END
from langgraph.graph import StateGraph


class MyState(TypedDict):
    # str_data:str
    # int_data:int
    # list_data:list[str]
    str_data :Annotated[str,operator.add]
    int_data:Annotated[int,operator.add]
    list_data:Annotated[List[str],operator.add]
    # test_data:Annotated[int,operator.mul]

# 定义一个更新节点，目的是将值返回到状态中
def update_node_1(state:MyState):
    print(f"节点1当前的状态为：{state}")
    return {
        "str_data":"这是node_1返回的结果",
        "int_data":1,
        "list_data":["这是node_1返回的结果"]
    }

def update_node_2(state:MyState):
    print(f"节点2当前的状态为：{state}")
    return {
        "str_data":"这是node_2返回的结果",
        "int_data":2,
        "list_data":["这是node_2返回的结果"]
    }

builder = StateGraph(state_schema = MyState)
builder.add_node(update_node_1)
builder.add_node(update_node_2)
builder.add_edge(START,"update_node_1")
builder.add_edge("update_node_1","update_node_2")
builder.add_edge("update_node_2",END)

graph = builder.compile()
result = graph.invoke({})
print(result)