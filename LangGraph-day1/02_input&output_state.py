# 此脚本用于演示状态的输入输出隔离
# 目的是规范什么状态可以作为输出，什么状态可以作为输出
from typing import TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph


# 1.定义出主状态
class MyState(TypedDict):
    query:str
    rag_result:str
    web_result:str
    final_answer:str
    extra_input:str
# 定义输入状态类
class InputSchema(TypedDict):
    query:str
# 定义输出状态类
class OutputSchema(TypedDict):
    final_answer:str
    extra_input: str
# 2.构建节点函数
def rag_search_node(state:MyState):
    query = state['query']
    rag_result = f"这是基于{query}构造的RAG模拟结果......QAQ"
    return {'rag_result':rag_result}

def web_search_node(state:MyState):
    query = state['query']
    web_result = f'这是基于{query}构造的web模拟结果......^_^'
    return {'web_result':web_result}

def final_answer_node(state:MyState):
    query = state['query']
    rag_result = state['rag_result']
    web_result = state['web_result']
    final_answer = f'基于{query}，RAG检索到了：{rag_result}，网络搜索到了：{web_result}'
    return {'final_answer':final_answer}

# 3.创建一个图的构造器对象
builder = StateGraph(state_schema = MyState,
                     input_schema = InputSchema,
                     output_schema = OutputSchema)
builder.add_node(rag_search_node)
builder.add_node(web_search_node)
builder.add_node(final_answer_node)

builder.add_edge(START,"rag_search_node")
builder.add_edge("rag_search_node","web_search_node")
builder.add_edge("web_search_node","final_answer_node")
# 最终到END的可写可不写
graph = builder.compile()
result = graph.invoke({"query":"atguigu","extra_input":"这是额外输入"})
print(result)