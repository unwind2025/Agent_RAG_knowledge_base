# 此脚本展示 LangGraph 节点级缓存策略的开启方式、原理以及缓存命中效果
# 核心：CachePolicy 是【节点粒度缓存】，不是整个图缓存；相同输入状态命中缓存时，节点不会重复执行
import time
from typing import TypedDict

# LangGraph 内存缓存实现（用于存放节点缓存结果）
from langgraph.cache.memory import InMemoryCache
# 内存持久化器（checkpointer，保存对话线程状态、历史快照，和cache是两套独立机制）
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
# CachePolicy：用来配置节点缓存规则（TTL、是否开启缓存等）
from langgraph.types import CachePolicy


# 定义图的状态结构
class MyState(TypedDict):
    x: int  # 输入数字
    result: int  # 计算结果


def node_1(state: MyState):
    """
    开启缓存的计算节点
    缓存命中条件（全部满足才命中）：
    1. 图结构、节点名称完全不变
    2. 到达这个节点时，该节点【依赖的输入状态】和缓存记录完全一致
    3. 缓存没有过期（由 CachePolicy 的 ttl 控制）
    ✅ 命中缓存：直接返回上次保存的输出，函数内部代码不会执行、不会sleep
    ❌ 未命中缓存：正常执行节点内逻辑，执行完成后把输出存入缓存
    """
    print(f"初始时的状态为：{state}")
    print("进入计算节点......")
    # 模拟耗时计算（3秒延时，用来直观感受缓存是否生效）
    time.sleep(3)
    print("计算完成！！！！！")
    x = state['x']
    # 返回增量更新字典：只更新 result 字段
    return {"result": x * 2}


def node_2(state: MyState):
    """未配置 cache_policy，不开启节点缓存，每次调用都会完整执行"""
    time.sleep(3)


# 构建状态图
builder = StateGraph(MyState)
# 添加节点 node_1，并给它绑定缓存策略
# ttl=1：缓存存活时间 1 秒，超过1秒缓存失效，需要重新计算
builder.add_node(node_1, cache_policy=CachePolicy(ttl=1))
# node_2 不设置 cache_policy，无缓存
builder.add_node(node_2)

# 构建流转链路：起点 → node_1 → node_2
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")

# ========== 缓存与checkpointer 配置 ==========
# InMemoryCache：内存缓存存储，节点CachePolicy的数据存在这里，程序重启缓存清空
cache = InMemoryCache()
# InMemorySaver：内存检查点，用于 thread 线程状态持久化，保存图每一步快照
# ⚠️ 重点区分：
# checkpointer 记录【图执行的历史状态、线程断点】，用于 resume 恢复执行
# cache（CachePolicy）记录【节点输入→节点输出的映射】，用于跳过重复计算，二者独立
checkpointer = InMemorySaver()

# 编译图，注入缓存对象和检查点
graph = builder.compile(cache=cache, checkpointer=checkpointer)

# 两个不同线程ID（不同thread_id代表两条独立会话）
config_1 = {"configurable": {"thread_id": "id_1"}}
config_2 = {"configurable": {"thread_id": "id_2"}}

# 第一次调用，thread_id=id_1，x=1：缓存不存在，执行node_1，耗时3s，执行后写入缓存
result_1 = graph.invoke({"x": 1}, config=config_1)
print(result_1)

# 第二次调用，thread_id=id_2，x=1：
# 节点缓存【不区分thread_id】！只要输入状态相同、缓存没过期，直接命中缓存，不会sleep 3秒
# 这是非常关键的特性：CachePolicy 是跨线程共享节点缓存
result_2 = graph.invoke({"x": 1}, config=config_2)
print(result_2)
