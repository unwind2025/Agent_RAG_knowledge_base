import operator
import os
import time
from typing import TypedDict, Annotated, List

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OpenAI_MODEL_ID"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=120,  # ChatOpenAI加长超时
    max_retries=3  # 开启底层sdk自动重试
)


# --- 1. 定义状态 ---
class State(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_step: str


# --- 2. 定义节点 ---

def node_input(state: State):
    """模拟接收用户输入"""
    return {
        "messages": [HumanMessage(content="请帮我写一段Python代码")],
        "current_step": "input_received"
    }


def node_processing(state: State, runtime: Runtime):
    """
    模拟中间处理过程，并使用 writer 输出自定义流式数据
    这对应 stream_mode="custom"
    """
    steps = ["正在分析意图...", "正在检索知识库...", "正在构建Prompt..."]
    writer = runtime.stream_writer
    for i, step in enumerate(steps):
        time.sleep(0.5)  # 模拟耗时操作

        # 使用 writer 发送自定义数据 (不影响图的状态)
        # 这些数据只能通过 stream_mode="custom" 接收到
        writer({
            "step_index": i + 1,
            "description": step,
            "timestamp": time.time()
        })

    return {"current_step": "processing_complete"}


def node_generation(state: State):
    """
    模拟 LLM 生成过程
    LangGraph 的 stream_mode="messages" 会自动捕获 LLM 的流式输出
    """

    # 调用 LLM
    response = llm.invoke(state["messages"])

    return {
        "messages": [response],
        "current_step": "generation_complete"
    }


# --- 3. 构建图 ---
builder = StateGraph(State)
builder.add_node("input", node_input)
builder.add_node("process", node_processing)
builder.add_node("generate", node_generation)

builder.add_edge(START, "input")
builder.add_edge("input", "process")
builder.add_edge("process", "generate")
builder.add_edge("generate", END)

graph = builder.compile()


# --- 4. 演示不同的流式输出模式 ---
def run_demo():
    initial_state = {"messages": [], "current_step": "start"}

    print(f"\n{'=' * 20} Mode: messages (输出 LLM Token) {'=' * 20}")
    print("描述: 输出 LLM 生成的消息片段 (Token)")
    # 注意：FakeListChatModel 默认是一次性返回，但在 messages 模式下会被包装成 chunk
    for chunk, metadata in graph.stream(initial_state, stream_mode="messages"):
        # chunk 是 BaseMessageChunk 对象
        # metadata 包含 node 信息
        node_name = metadata.get('langgraph_node', 'unknown')
        print(f"[{node_name}] Token: {chunk.content!r}")
        # print(chunk.content,end="")
        time.sleep(0.2)


if __name__ == "__main__":
    run_demo()
