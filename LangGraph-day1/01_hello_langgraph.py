# 此脚本用来演示LangGraph的基本搭建流程
# 模拟搭建一个搜索系统
from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph


# 1.定义状态
class MyState(TypedDict):
    query:str
    rag_result:str
    web_result:str
    final_answer:str

# 2.定义节点
def rag_search_node(state:MyState):
    # 从状态中获取查询内容
    query = state['query']
    # 模拟构建一个rag搜索结果
    rag_result = f'这是基于{query}的RAG搜索结果OvO'
    # 将处理后的值返回到相应的状态的值里面
    return {"rag_result":rag_result}

def web_search_node(state:MyState):
    # 从状态中获取数据
    query = state['query']
    # 模拟构建一个web搜索结果（函数中的具体业务逻辑）
    web_result = f'这是基于{query}的web搜索结果TAT'
    # 将处理后的结果返回到状态中
    return {'web_result':web_result}

def final_answer_node(state:MyState):
    # 从状态中获取数据
    query = state['query']
    rag_result = state['rag_result']
    web_result = state['web_result']
    # 模拟结果的构建
    final_answer = f'基于{query}，RAG检索到了：{rag_result}，网络搜索到了：{web_result}'
    # 将处理后的结果返回到状态中
    return {'final_answer':final_answer}

# 创建一个构造器对象，开始构造图结构
# 在创建的时候，首先传入状态的定义
builder = StateGraph(state_schema=MyState)
# 将构造好的节点放入构造器里面
builder.add_node("rag_search_node",rag_search_node)
builder.add_node(web_search_node)
builder.add_node(final_answer_node)
# 将注册进的节点通过边实现连接
builder.add_edge(START,"rag_search_node")
builder.add_edge("rag_search_node","web_search_node")
builder.add_edge("web_search_node","final_answer_node")
builder.add_edge("final_answer_node",END)
# 将构造器对象进行编译，得到一个可运行的图对象
graph = builder.compile()
# 调用图对象，通过invoke的方式传入一个初始的状态值
result = graph.invoke({'query':"哈哈，这是一个测试"})
print(result)


graph_structure = graph.get_graph()
res = graph_structure.draw_ascii()
print(res)
