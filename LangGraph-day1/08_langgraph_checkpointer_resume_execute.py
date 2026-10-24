# 此脚本演示 LangGraph 断点续跑功能：利用 SqliteSaver 将图的状态持久化到 SQLite，中断后可恢复执行
import sqlite3
from typing import TypedDict

# 基于SQLite的检查点存储，把每一步状态快照保存到磁盘数据库
from langgraph.checkpoint.sqlite import SqliteSaver
# START 是LangGraph内置常量，代表图的入口起点
from langgraph.constants import START
# StateGraph：状态图构建器，用来定义节点、边、状态流转逻辑
from langgraph.graph import StateGraph


# ---------------------- 定义图状态结构 ----------------------
# TypedDict 声明状态字典的字段，用于类型提示，LangGraph自动维护合并状态
class MyState(TypedDict):
    key_1: str
    key_2: str
    key_3: str


# ---------------------- 定义图节点 ----------------------
# 节点本质是函数：接收当前state，返回需要更新的状态字段字典
def node_1(state: MyState):
    # 打印进入节点时的状态，方便观察调试
    print(f"node_1的初始状态是：{state}")
    # 返回要更新的字段，LangGraph会自动合并到全局状态，不会覆盖其他key
    return {"key_1": "value_1"}


def node_2(state: MyState):
    print(f"node_2的初始状态是：{state}")
    # raise Exception("节点2报错啦！！！！！")  # 注释掉了异常，本次正常执行
    return {"key_2": "value_2"}


def node_3(state: MyState):
    print(f"node_3的初始状态是：{state}")
    return {"key_3": "value_3"}


# ---------------------- 初始化SQLite检查点 ----------------------
# 连接sqlite数据库文件，状态会持久化到磁盘，程序重启后数据不丢失
conn = sqlite3.connect(
    database="./sqlite_data/langgraph_sqlite",  # sqlite文件存放路径，不存在会自动创建
    check_same_thread=False  # 关闭线程检查，单脚本演示场景使用；多线程不推荐开启
)
# 实例化SqliteSaver，作为图的checkpointer，负责读写状态快照、实现断点恢复
memory = SqliteSaver(conn=conn)

# ---------------------- 搭建状态图拓扑 ----------------------
# 实例化图构建器，绑定我们定义好的状态类型 MyState
builder = StateGraph(MyState)

# 向图中注册3个节点，函数名即为节点名称
builder.add_node(node_1)
builder.add_node(node_2)
builder.add_node(node_3)

# 添加边，定义流转关系
builder.add_edge(START, "node_1")  # 图启动后，首先执行 node_1
builder.add_edge("node_1", "node_2")  # node_1执行完成，流向 node_2
builder.add_edge("node_1", "node_3")  # node_1执行完成，同时流向 node_3（并行分支）

# 编译图，传入checkpointer，开启状态持久化、断点续跑能力
graph = builder.compile(checkpointer=memory)

# ---------------------- 会话配置 ----------------------
# thread_id：会话唯一标识！同一个thread_id代表同一条执行链路，checkpointer靠它区分不同会话
config = {
    "configurable": {
        'thread_id': "777"
    }
}

# ---------------------- 执行图 ----------------------
# invoke：同步运行图；输入传None等价于空初始状态{}
# 因为绑定了SqliteSaver，每次运行都会读写该thread_id对应的检查点
result = graph.invoke(None, config=config)
