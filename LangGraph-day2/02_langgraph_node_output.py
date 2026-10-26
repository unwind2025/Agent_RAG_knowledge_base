# 此脚本展示 LangGraph 里【错误的返回模式】：直接 return state 原始对象带来的后果
# 核心知识点：LangGraph 节点规范 —— 节点应当返回【增量更新字典】，而不是直接返回传入的 state 对象
import operator
from typing import Annotated, List, TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph


# 定义图状态结构 MyState
class MyState(TypedDict):
    # 普通字段：无reducer，直接覆盖赋值
    str_data: str
    # 带 reducer: operator.add 的列表字段 → 含义是【追加合并】，而不是直接覆盖
    add_list_data: Annotated[List[str], operator.add]
    # 带 reducer: operator.add 的字符串字段 → 字符串拼接
    add_str_data: Annotated[str, operator.add]


def node_1(state: MyState):
    """节点1：直接修改传入的state字典，然后把state原对象return（不推荐写法）"""
    print("=== node_1 收到的 state ===")
    print(state)
    str_data = state['str_data']
    # 原地修改state里普通字段 str_data
    state['str_data'] = "node_1"
    # 原地修改带add reducer的列表字段
    state['add_list_data'] = ["1"]
    # state['add_str_data'] = "1"
    # ❌ 错误写法：直接返回原始state对象
    # LangGraph 预期：节点返回 {key: new_val} 增量更新字典，用来和旧state按reducer合并
    # 直接返回state会让合并逻辑行为混乱，不符合LangGraph设计范式
    return state


def node_2(state: MyState):
    """节点2，同样原地修改state并直接return state"""
    print("\n=== node_2 收到的 state ===")
    print(state)
    str_data = state['str_data']
    # state['str_data'] = "node_2"
    state['add_list_data'] = ["2"]
    return state


def node_3(state: MyState):
    """节点3，同样原地修改state并直接return state"""
    print("\n=== node_3 收到的 state ===")
    print(state)
    str_data = state['str_data']
    # state['str_data'] = "node_3"
    state['add_list_data'] = ["3"]
    return state


# 构建状态图
builder = StateGraph(MyState)
# 添加三个节点
builder.add_node(node_1)
builder.add_node(node_2)
builder.add_node(node_3)
# 设置边：起始 → node1 → node2 → node3 串行执行
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", "node_3")

# 编译图
graph = builder.compile()

# 初始输入状态
initial_input = {"str_data": "你好", "add_list_data": ["0"], "add_str_data": "1"}
# 调用图执行
result = graph.invoke(initial_input)

print("\n=== 最终返回结果 ===")
print(result)
