# 此脚本用于展示私有状态的设置，私有状态只是用于内部信息的传递，不参与初始的输入和最终的输出
from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph


# 主状态
class MyState(TypedDict):
    query:str
    final_answer:str

# 扩展部分，综合了一下输入输出隔离
class InputSchema(TypedDict):
    query:str
class OutputSchema(TypedDict):
    final_answer:str

# 私有状态,用于中间过程的数据传递，不参与最终的输出和初始的输入
class PrivateState(TypedDict):
    rag_result:str
    web_result:str

def rag_search_node(state:MyState):
    query = state['query']
    rag_result = f'这是基于{query}构造的RAG模拟结果......QAQ'
    return {'rag_result':rag_result}

def web_search_node(state:MyState):
    query = state['query']
    web_result = f'这是基于{query}构造的web模拟结果......^_^'
    return {'web_result':web_result}

# 这个最终汇总节点需要接收rag_result,一个web_result
def final_answer_node(state:PrivateState):
    rag_result = state['rag_result']
    web_result = state['web_result']
    final_answer = f'RAG检索到了：{rag_result}，网络搜索到了：{web_result}'
    return {"final_answer":final_answer}

# 创建构造器
builder = StateGraph(state_schema = MyState,
                     input_schema = InputSchema,
                     output_schema = OutputSchema)
builder.add_node(rag_search_node)
builder.add_node(web_search_node)
builder.add_node(final_answer_node)

builder.add_edge(START,'rag_search_node')
builder.add_edge('rag_search_node','web_search_node')
builder.add_edge('web_search_node','final_answer_node')
builder.add_edge('final_answer_node',END)

# 编译
graph = builder.compile()
result = graph.invoke({"query":"Atguigu123"})
print(result)