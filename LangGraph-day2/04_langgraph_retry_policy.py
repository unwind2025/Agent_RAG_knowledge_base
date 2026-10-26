# 这个脚本用于展示 LangGraph 节点的【重试策略 RetryPolicy】
# 适用场景：不稳定接口、临时网络抖动、偶尔报错的外部调用，短暂性故障可以靠重试自动恢复
from typing import TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph
# RetryPolicy：节点重试策略配置类，控制最大重试次数、哪些异常要重试、重试间隔等
from langgraph.types import RetryPolicy


# 定义图状态结构
class MyState(TypedDict):
    result: str


# 全局变量，记录当前函数被调用次数，用来模拟前两次失败、第三次成功
attempt_count = 0


def unstable_api_call(state: MyState):
    """模拟一个不稳定的外部API：前2次抛出异常失败，第3次返回成功结果"""
    global attempt_count
    attempt_count += 1
    print(f"运行第{attempt_count}次")

    # 前两次抛出异常，触发重试
    if attempt_count < 3:
        raise Exception(f"运行失败，这是第{attempt_count}次调用")
        # ValueError 无法通过重置来解决
        # raise ValueError(f"运行失败，这是第{attempt_count}次调用")
    else:
        # 第3次执行成功，返回状态增量字典
        return {"result": "运行成功！！"}


# 构建状态图
builder = StateGraph(MyState)
# 添加节点，绑定重试策略
# max_attempts=5：最多尝试5次（包含第一次原始执行 + 最多4次重试）
builder.add_node(unstable_api_call, retry_policy=RetryPolicy(max_attempts=5))
# 边：图启动后直接进入该不稳定节点
builder.add_edge(START, "unstable_api_call")

# 编译图
graph = builder.compile()

# 启动执行
result = graph.invoke({})
print(result)

print("1. 使用默认重试策略:")
print("   默认策略会对除特定异常外的所有异常进行重试")
print("   不会重试的异常包括: ValueError, TypeError, ArithmeticError, ImportError,")
print("                     LookupError, NameError, SyntaxError, RuntimeError,")
print("                     ReferenceError, StopIteration, StopAsyncIteration, OSError\n")
