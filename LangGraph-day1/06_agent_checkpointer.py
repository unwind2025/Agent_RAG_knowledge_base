# ============================================================
# 此案例用于演示 Agent 中的【检查点机制】
# 体现 LangGraph 中"状态持久化"的意义：
#   - 没有检查点：每次 invoke 都是全新的，agent 不记得上次对话
#   - 有检查点  ：agent 能跨调用"记住"之前的对话/中间状态
# ============================================================

import os

from dotenv import load_dotenv  # 读取 .env 里的环境变量（API Key 等）
from langchain.agents import create_agent  # 创建 Agent（较新 API）
from langchain_core.tools import tool  # 装饰器，把函数变成工具
from langchain_openai import ChatOpenAI  # OpenAI 兼容的模型客户端
from langgraph.checkpoint.memory import InMemorySaver  # 内存版检查点保存器

# 注释掉的旧版模型导入（可忽略）
# from langchain_community.chat_models import ChatOpenAI

# 加载 .env 中的环境变量
load_dotenv()

# ------------------------------------------------------------
# 配置大模型（这里接 DeepSeek）
#   - base_url : DeepSeek 的接口地址（从环境变量读取）
#   - api_key  : 调用密钥（从环境变量读取）
# 注释掉的 qwen 行说明可以换别的 OpenAI 兼容模型
# ------------------------------------------------------------
# llm = ChatOpenAI(model="qwen3.7-plus")
llm = ChatOpenAI(
    model=os.getenv("MODEL_ID"),  # DeepSeek 对话模型
    base_url=os.getenv("DEEPSEEK_BASE_URL"),  # DeepSeek 接口地址
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # DeepSeek 密钥
)


# ------------------------------------------------------------
# 定义一个工具：查天气
#   @tool 装饰器把普通函数注册为 Agent 可调用的"工具"
#   工具的描述（docstring）会被 Agent 看到，用于决定何时调用
# ------------------------------------------------------------
@tool
def weather_tool(city: str, date: str) -> str:
    """查天气的工具"""
    # 真实项目里这里会调用天气 API；本例直接返回模拟结果
    return f'{city}在{date}的天气是雷鸣电闪，还刮大风'


# ------------------------------------------------------------
# 【创建检查点保存器】
#   InMemorySaver：把检查点保存在"内存"中（进程结束即丢失）
#   另外还有持久化方案：SqliteSaver、PostgresSaver 等（存磁盘/数据库）
#   作用：把 agent 每次执行后的状态快照存起来，实现跨调用记忆
# ------------------------------------------------------------
checkpointer = InMemorySaver()

# ------------------------------------------------------------
# 创建 Agent
#   - model        : 驱动 agent 的大模型
#   - tools        : 提供给 agent 的工具列表
#   - checkpointer : 传入检查点保存器 → 启用状态持久化！
#                    （不传 checkpointer 的话，agent 就是"无记忆"的）
# ------------------------------------------------------------
agent = create_agent(
    model=llm,
    tools=[weather_tool],
    checkpointer=checkpointer,
)

# ------------------------------------------------------------
# 定义"会话配置"：通过 thread_id 标识【同一段会话】
#   - 同一个 thread_id 的多次调用 = 同一个会话，共享历史
#   - 不同的 thread_id          = 不同会话，互相隔离
#   检查点就是按 thread_id 来区分/保存不同会话的状态
# ------------------------------------------------------------
config = {
    "configurable": {
        "thread_id": "666"  # 给这个会话起个唯一 ID
    }
}

# ------------------------------------------------------------
# 【第一次调用】
#   agent 根据消息决定要不要调用工具：
#   用户问"深圳天气"→ agent 调用 weather_tool 拿到结果 → 组织回答
#   执行完后，整段状态（含对话历史）被保存到 checkpointer，
#   并关联到 thread_id = "666"
# ------------------------------------------------------------
response_1 = agent.invoke(
    input={"messages": "深圳在2026年6月24日的天气怎么样？"},
    config=config,
)
print('第一次调用', response_1['messages'][-1], end="\n\n==============\n\n")

# ------------------------------------------------------------
# 【第二次调用】
#   注意：用户这次只说"这个天气适合出门野餐吗"，
#   并没有重新说明"哪个天气/什么地点"。
#   【关键】因为使用了同一个 thread_id + checkpointer，
#   agent 能"回忆起"上一次对话里深圳7月3日的天气情况，
#   从而理解"这个天气"指的是什么，并基于它给出建议。
#   这就是检查点机制的意义：让 Agent 具备跨调用的上下文记忆。
# ------------------------------------------------------------
response_2 = agent.invoke(
    input={"messages": "这个天气适合出门野餐吗"},
    config=config,
)
print('第二次调用', response_2['messages'][-1], end="\n\n==============\n\n")
