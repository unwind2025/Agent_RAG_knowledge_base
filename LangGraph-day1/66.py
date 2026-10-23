
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()
llm = ChatOpenAI(model = "qwen3.7-plus")


@tool
def weather_tool(city:str,date:str) -> str:
    """查天气的工具"""
    return f"{city}在{date}的天气是雷雨大风天气"

checkpointer = InMemorySaver()
agent = create_agent(
    model = llm,
    tools = [weather_tool],
    checkpointer = checkpointer
)
config = {
    "configurable":{
        "thread_id":"atguigu"
    }
}

response_1 = agent.invoke(
    {"messages":"深圳在2026年7月3日的天气怎么样"},
    config = config
)
print('第一次调用',response_1['messages'][-1],end="\n\n==============\n\n")

response_2 = agent.invoke(
    {"messages":"可以出门野餐吗"},
    config = config
)
print('第二次调用',response_2['messages'][-1],end="\n\n==============\n\n")