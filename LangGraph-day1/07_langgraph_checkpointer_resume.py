# 此脚本展示：LangGraph 如何借助 Checkpointer（检查点），从上次运行断掉的位置恢复执行
# 核心原理：SqliteSaver 会把每一步图状态持久化到 SQLite 数据库；节点报错中断后，
# 再次invoke会读取历史检查点，跳过已经执行成功的节点，继续往下跑
import sqlite3
from typing import TypedDict

# LangGraph 检查点组件：基于 sqlite 的持久化存储，状态保存到磁盘数据库（区别于内存MemorySaver，重启程序数据也不丢）
from langgraph.checkpoint.sqlite import SqliteSaver
# 常量 START：图的起始入口标记
from langgraph.constants import START
# StateGraph：LangGraph 最核心的状态图构建器，用来定义节点、边、流转逻辑
from langgraph.graph import StateGraph


# -------------------------- 1. 定义图状态结构 --------------------------
# TypedDict：声明状态字典里有哪些key、用于类型提示，LangGraph会自动维护、合并状态
class MyState(TypedDict):
    key_1: str
    key_2: str
    key_3: str


# -------------------------- 2. 定义图中的节点（Node） --------------------------
# 节点本质就是一个函数：接收当前state，返回需要更新的state字段字典
def node_1(state: MyState):
    # 打印进入该节点时拿到的状态快照，方便调试查看状态流转
    print(f"node_1的初始状态是：{state}")
    # 返回字典：只写要更新的字段，LangGraph会自动合并到全局状态中，不会覆盖其他key
    return {"key_1": "value_1"}


def node_2(state: MyState):
    print(f"node_2的初始状态是：{state}")
    # 主动抛出异常，模拟节点执行失败、流程中断的场景
    # 中断后，node_1已经执行完成的状态会被SqliteSaver存入sqlite数据库
    raise Exception("节点2报错啦！！！！！")
    # 下面这行永远执行不到，仅作为示例正常返回
    return {"key_2": "value_2"}


def node_3(state: MyState):
    print(f"node_3的初始状态是：{state}")
    return {"key_3": "value_3"}


# -------------------------- 3. 初始化sqlite检查点存储 --------------------------
# 连接sqlite数据库文件，所有状态检查点都会写入这个db文件
conn = sqlite3.connect(
    database="./sqlite_data/langgraph_sqlite",  # 数据库文件路径，会自动创建
    check_same_thread=False  # 关闭线程校验，单脚本简单演示场景使用；多线程场景不建议开
)
# 实例化SqliteSaver，作为图的checkpointer，负责读写、持久化状态快照
memory = SqliteSaver(conn=conn)

# -------------------------- 4. 搭建状态图拓扑 --------------------------
# 实例化状态图构建器，绑定我们定义好的状态类型 MyState
builder = StateGraph(MyState)

# 向图中注册3个节点，函数名默认就是节点名称
builder.add_node(node_1)
builder.add_node(node_2)
builder.add_node(node_3)

# 添加边：定义节点流转关系
builder.add_edge(START, "node_1")  # 图启动后，第一个跑 node_1
builder.add_edge("node_1", "node_2")  # node_1执行完成 → 流向 node_2
builder.add_edge("node_1", "node_3")  # node_1执行完成 → 同时流向 node_3（并行分支！）

# 编译图，绑定检查点memory，开启状态持久化能力
# ✅ 重点：没有 checkpointer 就没有断点续跑功能
graph = builder.compile(checkpointer=memory)

# -------------------------- 5. 线程配置 config --------------------------
# thread_id 是会话唯一标识！非常关键
# 同一个 thread_id 代表同一次对话/同一条执行链路，SqliteSaver靠它区分不同会话的历史状态
config = {
    "configurable": {
        'thread_id': "777"
    }
}

# -------------------------- 6. 执行图 --------------------------
# invoke：同步执行图，传入初始空状态 {}，绑定会话config
# 第一次运行：node_1成功，然后并行进入 node_2、node_3；node_2抛异常中断
# 第二次再执行这一行：LangGraph读取sqlite里thread_id=777的检查点
# node_1已经跑完，不会重复执行，直接从失败的断点位置继续执行
result = graph.invoke({}, config=config)
