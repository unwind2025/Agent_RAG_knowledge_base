# 这个脚本用于展示节点的重试策略，在一些可以通过重试解决的问题时，开启此功能可以实现解决
from typing import TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy
from sqlalchemy.orm.base import state_str


class MyState(TypedDict):
    result:str

attempt_count = 0

def unstable_api_call(state:MyState):
    global attempt_count
    attempt_count += 1
    print(f"运行第{attempt_count}次")
    if attempt_count < 3:
        raise Exception(f"运行失败，这是第{attempt_count}次调用")
        # raise ValueError(f"运行失败，这是第{attempt_count}次调用")

    else:
        return{"result":"运行成功！！"}

builder = StateGraph(MyState)
builder.add_node(unstable_api_call,
                 retry_policy = RetryPolicy(max_attempts = 5))
builder.add_edge(START,"unstable_api_call")
graph = builder.compile()
result = graph.invoke({})
print(result)
print("1. 使用默认重试策略:")
print("   默认策略会对除特定异常外的所有异常进行重试")
print("   不会重试的异常包括: ValueError, TypeError, ArithmeticError, ImportError,")
print("                     LookupError, NameError, SyntaxError, RuntimeError,")
print("                     ReferenceError, StopIteration, StopAsyncIteration, OSError\n")
