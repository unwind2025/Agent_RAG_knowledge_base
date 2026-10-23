# 此脚本展示如何在LangGraph中上次运行断掉的地方恢复运行
import sqlite3
from typing import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.constants import START
from langgraph.graph import StateGraph

# 创建sqlite的检查点 -> 不是放在内存中，而是放在了数据库中
conn = sqlite3.connect(
    database="./sqlite_data/langgraph_sqlite",
    check_same_thread=False
)
memory = SqliteSaver(conn=conn)


class MyState(TypedDict):
    key_1:str
    key_2:str
    key_3:str

def node_1(state:MyState):
    print(f"node_1的初始状态是：{state}")
    return {"key_1":"value_1"}

def node_2(state:MyState):
    print(f"node_2的初始状态是：{state}")
    raise Exception("节点2报错啦！！！！！")
    return {"key_2":"value_2"}

def node_3(state:MyState):
    print(f"node_3的初始状态是：{state}")
    return {"key_3":"value_3"}

builder = StateGraph(MyState)
builder.add_node(node_1)
builder.add_node(node_2)
builder.add_node(node_3)
builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")
builder.add_edge("node_1","node_3")

graph = builder.compile(checkpointer=memory)
config = {
    "configurable":{
        'thread_id':"upguigu"
    }
}
result = graph.invoke({},config=config)