# ============================================================
# 本脚本用于演示 LangGraph 的基本搭建流程
# 场景：模拟搭建一个"搜索系统"，由 RAG 搜索 + 网络搜索 两条
#       检索链路并行/串行完成，最后汇总为最终答案。
# ============================================================

from typing import TypedDict  # 用于定义"状态"的类型（结构化字典）

# LangGraph 核心组件：
#   START  : 图的"入口"哨兵节点，所有执行都从它开始
#   END    : 图的"出口"哨兵节点，执行到它即代表整条链路结束
from langgraph.constants import START, END

# StateGraph：图构造器。通过它注册节点、添加边，最后 compile 出可执行图
from langgraph.graph import StateGraph


# ------------------------------------------------------------
# 1. 定义状态（State）
#    状态是整个图流转的"共享数据载体"：
#    - 每个节点都可以读取状态里的字段；
#    - 节点返回的 dict 会按 key 更新（合并）进状态，
#      供后续节点使用。
#    TypedDict 只是给状态做了类型标注（可选但推荐），
#    方便 IDE 提示和后期维护，运行时不强制。
# ------------------------------------------------------------
class MyState(TypedDict):
    query: str  # 用户输入的原始查询
    rag_result: str  # RAG 搜索返回的结果
    web_result: str  # 网络搜索返回的结果
    final_answer: str  # 最终汇总的答案


# ------------------------------------------------------------
# 2. 定义节点（Node）
#    节点就是一个普通函数，签名固定为：
#         def 节点名(state: MyState) -> dict
#    - 参数 state：当前最新的状态（可读取任意字段）
#    - 返回值：一个 dict，LangGraph 会把它"合并"进状态
#      （只更新 dict 中出现的 key，其余字段保持不变）
# ------------------------------------------------------------

def rag_search_node(state: MyState):
    """节点1：模拟 RAG（检索增强生成）搜索"""
    # 从状态中获取查询内容
    query = state['query']
    # 模拟构建一个 RAG 搜索结果（真实项目中这里会调用
    # 向量数据库/embedding 等检索逻辑）
    rag_result = f'这是基于{query}的RAG搜索结果OvO'
    # 将处理后的值返回到状态中（key 为 rag_result，
    # 会自动写入 MyState.rag_result）
    return {"rag_result": rag_result}


def web_search_node(state: MyState):
    """节点2：模拟网络搜索"""
    # 从状态中获取数据
    query = state['query']
    # 模拟构建一个 web 搜索结果（真实项目中这里会调用
    # 搜索引擎 API 等业务逻辑）
    web_result = f'这是基于{query}的web搜索结果TAT'
    # 将处理后的结果返回到状态中（写入 MyState.web_result）
    return {'web_result': web_result}


def final_answer_node(state: MyState):
    """节点3：汇总 RAG 与网络搜索结果，生成最终答案"""
    # 从状态中获取数据（此时 rag_result / web_result 都已被
    # 前面的节点写入，可以正常读取）
    query = state['query']
    rag_result = state['rag_result']
    web_result = state['web_result']
    # 模拟结果的构建：把两条检索结果拼接成最终答案
    final_answer = f'基于{query}，RAG检索到了：{rag_result}，网络搜索到了：{web_result}'
    # 将处理后的结果返回到状态中（写入 MyState.final_answer）
    return {'final_answer': final_answer}


# ------------------------------------------------------------
# 3. 构建图结构（StateGraph）
#    构造图分三步：创建构造器 → 注册节点 → 用边连接节点
# ------------------------------------------------------------

# (a) 创建构造器对象，开始构造图结构
#     创建时传入状态定义 state_schema=MyState，
#     让图知道数据长什么样
builder = StateGraph(state_schema=MyState)

# (b) 将节点注册进构造器
#     add_node 有两种用法：
#       - 显式命名：add_node("rag_search_node", rag_search_node)
#       - 隐式命名：add_node(web_search_node)
#         此时节点名取函数名本身（如 "web_search_node"）。
#     注意：后续 add_edge 引用节点时，用的名字必须和这里注册的名字一致
builder.add_node("rag_search_node", rag_search_node)  # 显式命名
builder.add_node(web_search_node)  # 隐式命名（函数名作节点名）
builder.add_node(final_answer_node)  # 隐式命名

# (c) 将注册的节点通过"边"连接起来，定义执行顺序
#     add_edge(起点, 终点)：从起点节点结束后，流转到终点节点
#     START 表示图的入口，END 表示图的出口
builder.add_edge(START, "rag_search_node")  # 图入口 → RAG搜索
builder.add_edge("rag_search_node", "web_search_node")  # RAG搜索 → 网络搜索
builder.add_edge("web_search_node", "final_answer_node")  # 网络搜索 → 最终汇总
builder.add_edge("final_answer_node", END)  # 最终汇总 → 图出口

# ------------------------------------------------------------
# 4. 编译图
#    把构造器编译成可运行的图对象。
#    编译之后才能被 invoke 调用，同时也能做序列化/可视化。
# ------------------------------------------------------------
graph = builder.compile()

# ------------------------------------------------------------
# 5. 调用图
#    通过 invoke 传入一个初始状态 dict，图会从 START 开始
#    按边的顺序依次执行节点，最后返回"完整的最新状态"。
#    （也可以只拿某个字段，如 result['final_answer']）
# ------------------------------------------------------------
result = graph.invoke({'query': "哈哈，这是一个测试"})
print(result)

# ------------------------------------------------------------
# 6. （可选）可视化图结构
#    get_graph() 拿到图的结构信息，draw_ascii() 在控制台
#    用字符画打印出节点和边的拓扑结构，方便查看执行流程。
# ------------------------------------------------------------
graph_structure = graph.get_graph()
res = graph_structure.draw_ascii()
print(res)
