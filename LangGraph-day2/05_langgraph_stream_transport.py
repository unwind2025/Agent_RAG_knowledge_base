# 这个脚本用于展示LangGraph中的流式输出，在每个节点运行完之后，输出该节点返回的状态信息等
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

load_dotenv()
llm = ChatOpenAI(model="qwen3.7-plus")

class MyState(TypedDict):
    value_1:str
    value_2:str
    value_3:str


def node_1(state:MyState,runtime:Runtime):
    writer = runtime.stream_writer
    writer({
        "node_name":"node_1",
        "status":"succeed",
        "description":"节点一运行成功"
    })
    llm.invoke("你觉得先有鸡还是先有蛋")
    return {"value_1":"111"}
def node_2(state:MyState,runtime:Runtime):
    writer = runtime.stream_writer
    writer({
        "node_name":"node_2",
        "status":"succeed",
        "description":"节点二运行成功"
    })
    return {"value_2":"222"}
def node_3(state:MyState,runtime:Runtime):
    writer = runtime.stream_writer
    writer({
        "node_name":"node_3",
        "status":"succeed",
        "description":"节点三运行成功"
    })
    return {"value_3":"333"}

builder = StateGraph(MyState)
builder.add_node(node_1)
builder.add_node(node_2)
builder.add_node(node_3)
builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")
builder.add_edge("node_2","node_3")
graph = builder.compile()

# for event in graph.stream({},stream_mode = "values"):
#     print(event)
# for event in graph.stream({},stream_mode = "updates"):
#     print(event)
# for event in graph.stream({},stream_mode = "debug"):
#     print(event)
# for event in graph.stream({},stream_mode = "custom"):
#     print(event)
# for event in graph.stream({},stream_mode =["updates","custom","debug"]):
#     print(event)
for event in graph.stream({},stream_mode ="messages"):
    print(event)