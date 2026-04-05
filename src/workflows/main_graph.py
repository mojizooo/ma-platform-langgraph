# src/workflows/main_graph.py
from typing import Literal
import os
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.state.graph_state import AgentState
from src.core.base_agent import BaseAgent
# 假设组员们在 src/tools 和 src/agents 下实现了具体的工具和智能体
# from src.tools.web_search import WebSearchTool 
# from src.tools.ocsr_parser import OCSRTool

# 1. 准备工具箱
# 这里体现了极高的通用性，任何人写的工具只要继承了 BaseTool 都可以放到这个列表里
global_tools = []

# 2. 定义工具执行节点
# LangGraph 原生支持 ToolNode，它会自动读取状态中最新的 tool_calls 并执行相应工具
tool_node = ToolNode(global_tools)

# 3. 定义路由逻辑 (Router)
def router(state: AgentState) -> Literal["tools", "__end__", "continue"]:
    """
    这是一个条件路由函数，决定下一步去哪。
    """
    messages = state.get("messages", [])
    if not messages:
        return "__end__"
        
    last_message = messages[-1]
    
    # 如果最新的消息包含了工具调用请求，则将图路由到工具节点
    if last_message.tool_calls:
        return "tools"
        
    # 如果没有工具调用，判断任务是否完成（这里可以根据具体的标志位或大模型的输出来判断）
    # 简单起见，如果大模型输出了特定的结束语（如 "FINAL ANSWER"），就结束
    if "FINAL ANSWER" in last_message.content:
        return "__end__"
        
    # 否则继续循环（或交还给 Supervisor）
    return "continue"

# 4. 实例化智能体 (节点)
# 这里以一个总控大模型（Supervisor/Researcher）为例。
# 在实际的小组开发中，你们可以实例化多个 BaseAgent，比如 planner, coder, reviewer 等。

# 确保 API 密钥存在
api_key = os.getenv("QWEN_API_KEY")
if not api_key:
    raise ValueError("QWEN_API_KEY 环境变量未设置")

llm = ChatOpenAI(
    model=os.getenv("QWEN_MODEL", "qwen3.5-plus"),
    api_key=api_key,
    base_url=os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
)

primary_agent = BaseAgent(
    name="Researcher",
    llm=llm,
    tools=global_tools,
    system_prompt="你是一个核心研究助手。你可以使用工具来获取信息。完成任务后，请在回复末尾加上 'FINAL ANSWER'。"
)

# 包装一下 Agent 的调用，适配 LangGraph 的节点格式
def call_primary_agent(state: AgentState):
    return primary_agent(state)

# 5. 构建状态图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("Researcher", call_primary_agent)
workflow.add_node("tools", tool_node)

# 添加边与流转逻辑
# 起点直接连到 Researcher
workflow.add_edge(START, "Researcher")

# Researcher 结束后，经过条件路由判断去向
workflow.add_conditional_edges(
    "Researcher",
    router,
    {
        "tools": "tools",        # 去执行工具
        "__end__": END,          # 结束任务
        "continue": "Researcher" # 没结束的话继续思考（或者交给下一个 Agent）
    }
)

# 工具节点执行完毕后，状态会自动更新（包含工具输出），必须强制流转回 Researcher 继续判断
workflow.add_edge("tools", "Researcher")

# 6. 编译生成最终的可执行图
# 可以在此处添加 memory（例如 SqliteSaver），以便支持多轮对话的时间旅行和断点调试
app = workflow.compile()