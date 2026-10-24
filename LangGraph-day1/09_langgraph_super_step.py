# 此脚本通过一个较复杂的图结构，演示 LangGraph 的底层调度原理（并行分支、状态合并、reducer 注解）
import operator
from typing import TypedDict, Annotated, List

# LangGraph内置常量，代表图的起始入口
from langgraph.constants import START, END
# 状态图构建器，用来定义节点、边、流转关系
from langgraph.graph import StateGraph


# -------------------------- 定义状态 MyState --------------------------
class MyState(TypedDict):
    # Annotated：给字段附加归约函数（reducer）
    # data_list 是字符串列表，归约函数是 operator.add
    # 含义：多个节点同时返回 data_list 时，不会互相覆盖，而是做列表拼接 +=
    # 如果不写 Annotated[..., operator.add]，后返回的值会直接覆盖前面的值
    data_list: Annotated[List[str], operator.add]  # 追加列表


# -------------------------- 定义各个节点 --------------------------
def a(state: MyState):
    """节点a：图的第一个节点，往列表添加 "a" """
    return {"data_list": ["a"]}


def b_1(state: MyState):
    """分支b链路第1步"""
    return {"data_list": ["b_1"]}


def b_2(state: MyState):
    """分支b链路第 2步，b_1执行完才走到这里"""
    return {"data_list": ["b_2"]}


def c(state: MyState):
    """分支 c链路节点，a 执行完和 b_1并行触发"""
    return {"data_list": ["c"]}


def d(state: MyState):
    """汇聚节点：必须等 b_2 和 d 的上游 c 两条分支全部完成，才会执行d"""
    return {"data_list": ["d"]}


# -------------------------- 搭建图拓扑 --------------------------
builder = StateGraph(MyState)
# 注册所有节点
builder.add_node(a)
builder.add_node(b_1)
builder.add_node(b_2)
builder.add_node(c)
builder.add_node(d)

# 定义边，画出整个图：
# START → a
builder.add_edge(START, "a")
# a 出来两条并行分支：
# 分支1：a → b_1 → b_2 → d
builder.add_edge("a", "b_1")
builder.add_edge("b_1", "b_2")
# 分支2：a → c → d
builder.add_edge("a", "c")
builder.add_edge("c", "d")
# b_2执行完流向d
builder.add_edge("b_2", "d")
builder.add_edge("d", END)

# 编译图，这里没有加checkpointer，不做持久化断点保存
graph = builder.compile()

# 启动图，传入空初始状态
result = graph.invoke({})
print(result)

"""
图结构梳理：
        ┌──> b_1 ──> b_2 ──┐
START → a                  ├─> d
        └──> c ────────────┘

👉 LangGraph 调度规则：
1. a执行完，同时触发 b_1 和 c（并行执行）
2. d 是汇聚节点：需要等待它所有前驱（b_2、c）全部完成，d才会跑
3. 因为是并行，b_1-b_2 和 c 的执行顺序不固定！
所以最终顺序可能是：
[A] [a,b_1,b_2,c,d]
[B] [a,c,b_1,b_2,d]
[C] [a,b_1,c,b_2,d]
这三种都有可能，取决于线程调度快慢
✅ 正确答案：ABC都有可能，不是固定顺序
"""
