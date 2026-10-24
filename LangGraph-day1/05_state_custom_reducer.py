# ============================================================
# 此脚本用于展示 LangGraph 中的【自定义 reducer 函数】
# 要点：
#   - 除了内置 operator.add，你可以写任意自定义函数作为 reducer
#   - reducer 函数签名约定：def 名(旧值, 新值) -> 合并后的值
#   - 每次"状态已有旧值 + 节点再写入"时，就会调用它
# ============================================================

import operator  # 内置运算符（add/mul 等）
from typing import TypedDict, Annotated, List  # Annotated 绑定 reducer

from langgraph.constants import START, END
from langgraph.graph import StateGraph


# ------------------------------------------------------------
# 【自定义 reducer 函数】
# 参数约定（LangGraph 固定传入两个参数）：
#   1. 第一个参数 = 当前状态里已有的值（旧值）
#   2. 第二个参数 = 节点这次新返回的值（新值）
# 返回值 = 合并后的最终值，会被写回状态
# ------------------------------------------------------------
def custom_reducer(origin_value: int, new_value: int):
    # 自定义合并规则：旧值乘 3 + 新值乘 2
    return origin_value * 3 + new_value * 2


# ------------------------------------------------------------
# 定义主状态
#   - str_data  / list_data 用内置 operator.add（拼接/追加）
#   - int_data  用我们【自定义】的 custom_reducer
# ------------------------------------------------------------
class MyState(TypedDict):
    # ---- 注释掉的普通类型写法（直接覆盖） ----
    # str_data: str
    # int_data: int
    # list_data: list[str]

    str_data: Annotated[str, operator.add]  # 字符串拼接
    int_data: Annotated[int, custom_reducer]  # 使用自定义 reducer！
    list_data: Annotated[List[str], operator.add]  # 列表追加
    # test_data: Annotated[int, operator.mul]      # 乘法示例（注释掉）


# ------------------------------------------------------------
# 节点1：第一次写入
#   此时状态里还没有 int_data 等字段（初始为 {}），
#   所以这些值会【直接存储】，自定义 reducer 此时不会被触发。
# ------------------------------------------------------------
def update_node_1(state: MyState):
    print(f"节点1当前的状态为：{state}")  # 打印：{}
    return {
        "str_data": "这是node_1返回的结果",  # 首次写入，直接存
        "int_data": 1,  # 首次写入，int_data = 1
        "list_data": ["这是node_1返回的结果"]  # 首次写入，直接存
    }


# ------------------------------------------------------------
# 节点2：第二次写入
#   【关键】int_data 已有旧值 1，此刻会调用自定义 reducer：
#     custom_reducer(旧值=1, 新值=2)
#       = 1 * 3 + 2 * 2
#       = 3 + 4
#       = 7
#   str_data / list_data 则继续走 operator.add（拼接/追加）
# ------------------------------------------------------------
def update_node_2(state: MyState):
    print(f"节点2当前的状态为：{state}")  # 打印：{..., 'int_data': 1, ...}
    return {
        "str_data": "这是node_2返回的结果",
        "int_data": 2,  # 触发 custom_reducer(1, 2)
        "list_data": ["这是node_2返回的结果"]
    }


# ------------------------------------------------------------
# 构建图：节点1 → 节点2（串行）
# ------------------------------------------------------------
builder = StateGraph(state_schema=MyState)
builder.add_node(update_node_1)
builder.add_node(update_node_2)
builder.add_edge(START, "update_node_1")
builder.add_edge("update_node_1", "update_node_2")
builder.add_edge("update_node_2", END)

# 编译并调用（空初始状态）
graph = builder.compile()
result = graph.invoke({})  # 传入空 dict，所有字段从零开始
print(result)
