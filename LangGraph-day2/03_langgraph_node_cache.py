# 此脚本展示了LangGraph中节点如何开启缓存策略，以及缓存策略的效果
import time
from typing import TypedDict
from langgraph.cache.memory import InMemoryCache
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.types import CachePolicy


class MyState(TypedDict):
    x:int
    result:int

# 进入此节点之前，状态为{"x":1}
# 如何击中缓存：
# 1.图结构和映射名全都不变；
# 2.运行到该开启缓存的节点时，状态和之前创建缓存时一致
def node_1(state:MyState):
    print(f"初始时的状态为：{state}")
    print("进入计算节点......")
    time.sleep(3)
    print("计算完成！！！！！")
    x = state['x']
    return {"result": x*2}

def node_2(state:MyState):
    time.sleep(3)

builder = StateGraph(MyState)
builder.add_node(node_1,cache_policy = CachePolicy(ttl=1))
builder.add_node(node_2)
builder.add_edge(START,"node_1")
builder.add_edge("node_1","node_2")


cache = InMemoryCache()
checkpointer = InMemorySaver()
graph = builder.compile(cache = cache,checkpointer = checkpointer)

config_1 = {"configurable":{"thread_id":"id_1"}}
config_2 = {"configurable":{"thread_id":"id_2"}}

result_1 = graph.invoke({"x":1},config=config_1)
print(result_1)
result_2 = graph.invoke({"x":1},config=config_2)
print(result_2)