# ============================================================
# 此脚本用于演示 LangGraph 中"状态的输入输出隔离"
# 目的：规范——
#       1) 图允许接收哪些字段作为"输入"（input_schema）
#       2) 图最终对外暴露哪些字段作为"输出"（output_schema）
#       3) 图内部流转时完整使用哪些字段（state_schema）
# ============================================================

from typing import TypedDict  # 用 TypedDict 定义结构化状态类型
from langgraph.constants import START  # 图的入口哨兵节点
from langgraph.graph import StateGraph  # 图构造器


# ------------------------------------------------------------
# 1. 定义"主状态"（state_schema）
#    这是图"内部"完整使用的状态：所有节点读写都基于它。
#    它包含输入、中间结果、最终结果、额外字段等全部内容，
#    相当于"图的内部全量数据模型"。
# ------------------------------------------------------------
class MyState(TypedDict):
    query: str  # 用户的原始查询（由输入进入）
    rag_result: str  # RAG 搜索结果（内部中间变量）
    web_result: str  # 网络搜索结果（内部中间变量）
    final_answer: str  # 最终答案（对外输出）
    extra_input: str  # 一个"额外输入"字段，用于演示
    # 输入里有、但输出 schema 是否包含的差异


# ------------------------------------------------------------
# 定义"输入状态"（input_schema）
#    只声明图"允许接收"哪些字段。
#    在 invoke 时传入的 dict 会被 input_schema 校验/约束，
#    防止调用方塞入图不想接收的数据。
#    这里只接收 query 和 extra_input（extra_input 因有默认在 TypedDict 里是可选的），rag_result 等内部字段不会出现在输入。
# ------------------------------------------------------------
class InputSchema(TypedDict):
    query: str


# 注意：示例代码里 InputSchema 只定义了 query，
#       但 invoke 传入了 extra_input —— LangGraph 对多余字段
#       默认是"放行"（不报错，extra_input 仍会进入状态），
#       这点在文末会细讲。

# ------------------------------------------------------------
# 定义"输出状态"（output_schema）
#    只声明图"对外暴露"哪些字段。
#    invoke 返回的结果 dict，会按 output_schema 过滤——
#    内部状态里的 rag_result、web_result 等即使存在，
#    只要不在 output_schema 中，就不会出现在返回值里。
# ------------------------------------------------------------
class OutputSchema(TypedDict):
    final_answer: str
    extra_input: str


# ------------------------------------------------------------
# 2. 构建节点函数
#    节点签名统一为：def 节点名(state: MyState) -> dict
#    参数是主状态（内部全量），返回值按 key 合并进主状态。
# ------------------------------------------------------------

def rag_search_node(state: MyState):
    """节点1：模拟 RAG 搜索"""
    query = state['query']  # 读取主状态中的查询
    rag_result = f"这是基于{query}构造的RAG模拟结果......QAQ"
    return {'rag_result': rag_result}  # 写回主状态


def web_search_node(state: MyState):
    """节点2：模拟网络搜索"""
    query = state['query']
    web_result = f'这是基于{query}构造的web模拟结果......^_^'
    return {'web_result': web_result}  # 写回主状态


def final_answer_node(state: MyState):
    """节点3：汇总生成最终答案"""
    query = state['query']
    rag_result = state['rag_result']  # 读取前面节点写入的中间结果
    web_result = state['web_result']
    final_answer = f'基于{query}，RAG检索到了：{rag_result}，网络搜索到了：{web_result}'
    return {'final_answer': final_answer}  # 写回主状态


# ------------------------------------------------------------
# 3. 创建图构造器
#    关键点：同时传入三个 schema，实现"内外隔离"
#      - state_schema : 内部全量状态（节点间流转用）
#      - input_schema : 对外输入约束
#      - output_schema: 对外输出过滤
#    三者可以不同，LangGraph 会做自动"转换/过滤"。
# ------------------------------------------------------------
builder = StateGraph(
    state_schema=MyState,  # 内部状态
    input_schema=InputSchema,  # 输入层
    output_schema=OutputSchema,  # 输出层
)

# 注册节点（隐式命名，节点名=函数名）
builder.add_node(rag_search_node)
builder.add_node(web_search_node)
builder.add_node(final_answer_node)

# 用边连接节点，定义执行顺序（串行流水线）
builder.add_edge(START, "rag_search_node")  # 入口 → RAG
builder.add_edge("rag_search_node", "web_search_node")  # RAG → web
builder.add_edge("web_search_node", "final_answer_node")  # web → 汇总
# 注意：这里没有显式连到 END。
# 只要最后一个节点执行完、没有可流转的下游边，图会自然结束，
# 所以"到 END 可写可不写"。但更规范、更明确的写法是补上：
#   builder.add_edge("final_answer_node", END)

# 编译图
graph = builder.compile()

# 调用图：invoke 传入的 dict 对应 input_schema 的字段
result = graph.invoke({"query": "atguigu", "extra_input": "这是额外输入"})
print(result)
