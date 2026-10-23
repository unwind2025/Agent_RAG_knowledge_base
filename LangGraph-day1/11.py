from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph


class MyState(TypedDict):
    query:str
    rag_result:str
    web_result:str
    final_result:str

def rag_search_node(state:MyState):
    query = state["query"]
    rag_result = f"这是基于{query}的RAG搜索结果ovo"
    return {"rag_result":rag_result}

def web_search_node(state:MyState):
    query = state["query"]
    web_result = f"这是基于{query}的web搜索结果TAT"
    return {"web_result":web_result}

def final_search_node(state:MyState):
    query = state["query"]
    rag_result = state["rag_result"]
    web_result = state["web_result"]
    final_answer = f"基于{query}，RAG搜索到了：{rag_result},web搜索到了{web_result}"
    return {"final_result":final_answer}

builder = StateGraph(state_schema=MyState)
builder.add_node(rag_search_node)
builder.add_node(web_search_node)
builder.add_node(final_search_node)

builder.add_edge(START,"rag_search_node")
builder.add_edge("rag_search_node","web_search_node")
builder.add_edge("web_search_node","final_search_node")
builder.add_edge("final_search_node",END)

graph = builder.compile()

result = graph.invoke({"query":"测试今天的天气"})
print(result)


graph_structure = graph.get_graph()
res = graph_structure.draw_ascii()
print(res)