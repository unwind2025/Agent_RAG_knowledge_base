# ============================================================
# 此脚本用于展示 LangGraph 中"状态的更新方式"设置
# 核心概念：Reducer（更新函数/聚合器）
#   - 默认情况下，节点返回某字段 = 直接【覆盖】该字段
#   - 但用 Annotated[类型, 更新函数] 声明后，
#     节点返回值会先经过"更新函数"再写回状态，
#     从而实现【累加 / 追加 / 相乘】等自定义更新逻辑
# ============================================================

import operator  # 内置运算符模块，提供 add/mul 等函数
from typing import TypedDict, Annotated, List  # Annotated 用于绑定 reducer

from langgraph.constants import START, END
from langgraph.graph import StateGraph


# ------------------------------------------------------------
# 定义主状态
# 关键语法：Annotated[基础类型, reducer函数]
#   reducer 函数的签名约定：reducer(旧值, 新值) -> 新合并值
# ------------------------------------------------------------
class MyState(TypedDict):
    # ---- 以下是被注释掉的"普通类型"写法 ----
    # str_data: str            # 普通类型：节点返回值直接覆盖
    # int_data: int            # 普通类型：直接覆盖
    # list_data: list[str]     # 普通类型：直接覆盖

    # ---- 实际使用的 Reducer 写法 ----
    # 用 operator.add 作为 reducer：
    #   str_data  : 字符串拼接（str + str）
    #   int_data  : 数值相加（int + int）
    #   list_data : 列表拼接/追加（list + list）
    str_data: Annotated[str, operator.add]  # 字符串累加
    int_data: Annotated[int, operator.add]  # 整数累加
    list_data: Annotated[List[str], operator.add]  # 列表追加

    # 另一个 reducer 示例（被注释）：用乘法
    # test_data: Annotated[int, operator.mul]      # 若启用，1 * 2 = 2


# ------------------------------------------------------------
# 节点1：第一次往状态里写入值
#   注意：这是【第一次写入】，此时状态里还没有这些字段，
#   所以会【直接存储】，reducer 不会被"对空值"触发。
# ------------------------------------------------------------
def update_node_1(state: MyState):
    print(f"节点1当前的状态为：{state}")  # 进入时状态还是空的 {}
    return {
        "str_data": "这是node_1返回的结果",
        "int_data": 1,
        "list_data": ["这是node_1返回的结果"]
    }


# ------------------------------------------------------------
# 节点2：第二次往状态里写入值
#   【关键】：此时这些字段已经有值了，
#   LangGraph 会调用 reducer = operator.add 合并：
#     - str_data  = 旧字符串 + 新字符串   （拼接）
#     - int_data  = 旧整数 + 新整数       （相加）
#     - list_data = 旧列表 + 新列表       （追加元素）
# ------------------------------------------------------------
def update_node_2(state: MyState):
    print(f"节点2当前的状态为：{state}")  # 这里能看到节点1写入后的值
    return {
        "str_data": "这是node_2返回的结果",
        "int_data": 2,
        "list_data": ["这是node_2返回的结果"]
    }


# ------------------------------------------------------------
# 构建图：串行执行 节点1 → 节点2
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
