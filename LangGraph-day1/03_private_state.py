# ============================================================
# 此脚本用于展示 LangGraph 的"私有状态"设置
# 核心思想：
#   - 私有状态只用于"内部信息传递"
#   - 它【不参与】初始输入，也【不参与】最终输出
#   - 它只对"声明使用它的节点"可见，其余节点读不到
# ============================================================

from typing import TypedDict
from langgraph.constants import START, END  # 图的入口/出口哨兵
from langgraph.graph import StateGraph


# ------------------------------------------------------------
# 【主状态】MyState —— 整个图"对外"的状态
#   - 是所有节点默认读写的基础状态
#   - 也是输入/输出 schema 与它做映射的对象
# ------------------------------------------------------------
class MyState(TypedDict):
    query: str  # 用户查询（来自输入）
    final_answer: str  # 最终答案（对外输出）


# ------------------------------------------------------------
# 【输入状态】InputSchema —— 图允许接收的字段
# ------------------------------------------------------------
class InputSchema(TypedDict):
    query: str


# ------------------------------------------------------------
# 【输出状态】OutputSchema —— 图对外暴露的字段
# ------------------------------------------------------------
class OutputSchema(TypedDict):
    final_answer: str


# ------------------------------------------------------------
# 【私有状态】PrivateState —— 只用于中间过程的数据传递
#   - 包含 rag_result、web_result 两个"中间变量"
#   - 它们【不进】初始输入，也【不进】最终输出
#   - 只有显式以 PrivateState 作为类型标注的节点才看得到
# ============================================================
class PrivateState(TypedDict):
    rag_result: str  # RAG 搜索结果（中间量）
    web_result: str  # 网络搜索结果（中间量）


# ------------------------------------------------------------
# 节点1：模拟 RAG 搜索
#   类型标注是 MyState（主状态）→ 读写的是主状态
#   返回 {'rag_result': ...}，虽然 rag_result 不在 MyState 里，
#   但 LangGraph 允许节点返回"额外字段"，
#   这些字段会被放入私有通道（供后续私有节点使用）
# ------------------------------------------------------------
def rag_search_node(state: MyState):
    query = state['query']  # 读主状态的 query
    rag_result = f'这是基于{query}构造的RAG模拟结果......QAQ'
    return {'rag_result': rag_result}  # 写入"额外字段"→ 进入私有通道


# ------------------------------------------------------------
# 节点2：模拟网络搜索（同上）
# ------------------------------------------------------------
def web_search_node(state: MyState):
    query = state['query']
    web_result = f'这是基于{query}构造的web模拟结果......^_^'
    return {'web_result': web_result}  # 同样进入私有通道


# ------------------------------------------------------------
# 节点3：最终汇总节点
#   【关键】：这个节点的类型标注是 PrivateState，而不是 MyState！
#   LangGraph 会因此为它开辟一个"私有状态通道"：
#     - 它能读取 rag_result、web_result（来自前面节点的额外返回值）
#     - 它读不到主状态里不该有的东西，只按 PrivateState 暴露的字段来
#   final_answer 虽然不在 PrivateState 里，但返回值照样会
#   合并回主状态（因为主状态 MyState 里有 final_answer 这个字段）
# ------------------------------------------------------------
def final_answer_node(state: PrivateState):
    rag_result = state['rag_result']  # 读私有通道里的 RAG 结果
    web_result = state['web_result']  # 读私有通道里的 web 结果
    final_answer = f'RAG检索到了：{rag_result}，网络搜索到了：{web_result}'
    return {"final_answer": final_answer}  # 写回主状态的 final_answer


# ------------------------------------------------------------
# 创建构造器
#   - state_schema  : MyState（主状态）
#   - input_schema  : InputSchema（输入约束）
#   - output_schema : OutputSchema（输出过滤）
#   注意：这里没有显式传入 PrivateState，
#   LangGraph 会根据"节点函数类型标注"自动识别私有状态。
# ------------------------------------------------------------
builder = StateGraph(
    state_schema=MyState,
    input_schema=InputSchema,
    output_schema=OutputSchema,
)

# 注册节点（隐式命名）
builder.add_node(rag_search_node)
builder.add_node(web_search_node)
builder.add_node(final_answer_node)

# 连接节点（串行流水线：入口→RAG→web→汇总→出口）
builder.add_edge(START, 'rag_search_node')
builder.add_edge('rag_search_node', 'web_search_node')
builder.add_edge('web_search_node', 'final_answer_node')
builder.add_edge('final_answer_node', END)

# 编译
graph = builder.compile()

# 调用：invoke 传入的 dict 对应 input_schema（只有 query）
result = graph.invoke({"query": "Atguigu123"})
print(result)
