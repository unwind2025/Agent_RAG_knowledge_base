from typing import TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph


class MyState(TypedDict):
    query: str
    rag_result: str
    web_result: str
    final_answer: str
    extra_input:str
class InputSchema(TypedDict):
    query: str

class OutputSchema(TypedDict):
    final_answer: str
    extra_input: str

def rag_search_node(state:MyState):
    query =  state["query"]
    rag_result = f"这是基于{query}构造的RAG模拟结果"
    return {"rag_result": rag_result}

def web_search_node(state:MyState):
    query = state["query"]
    web_result = f"这是基于{query}构造的web模拟结果"
    return {"web_result": web_result}

def final_search_node(state:MyState):
    query = state["query"]
    rag_result = state["rag_result"]
    web_result = state["web_result"]
    final_answer = f"这是基于{query},RAG检索到了：{rag_result},web检索到了:{web_result}"
    return {"final_answer": final_answer}

builder = StateGraph(state_schema=MyState,
                     input_schema= InputSchema,
                     output_schema= OutputSchema)

builder.add_node(rag_search_node)
builder.add_node(web_search_node)
builder.add_node(final_search_node)

builder.add_edge(START,"rag_search_node")
builder.add_edge("rag_search_node","web_search_node")
builder.add_edge("web_search_node","final_search_node")

graph = builder.compile()
result = graph.invoke({"query":"atguigu","extra_inpput":"这是额外输入"})
print(result)
