from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph


# 主状态
class MyState(TypedDict):
    query: str
    final_answer: str

class InputSchema(TypedDict):
    query: str
class OutputSchema(TypedDict):
    final_answer: str

# 私有状态
class PrivateState(TypedDict):
    rag_result: str
    web_result: str

def rag_search_node(state:MyState):
    query = state["query"]
    rag_result = f"这是基于{query}构造的RAG模拟结果....qaq"
    return {"rag_result": rag_result}

def web_search_node(state:MyState):
    query = state["query"]
    web_result = f"这是基于{query}构造的web模拟结果....^_^"
    return {"web_result": web_result}

def final_answer_node(state:PrivateState):
    rag_result = state["rag_result"]
    web_result = state["web_result"]
    final_answer = f"这是基于{rag_result}和{web_result}构造的最终答案...."
    return {"final_answer": final_answer}

builder = StateGraph(state_schema=MyState,input_schema=InputSchema,output_schema=OutputSchema)
builder.add_node(rag_search_node)
builder.add_node(web_search_node)
builder.add_node(final_answer_node)

builder.add_edge(START,"rag_search_node")
builder.add_edge("rag_search_node","web_search_node")
builder.add_edge("web_search_node","final_answer_node")
builder.add_edge("final_answer_node",END)

graph = builder.compile()
result = graph.invoke({"query":"Atguigu1234"})
print(result)

