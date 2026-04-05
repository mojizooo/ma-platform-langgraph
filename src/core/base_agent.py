# src/core/base_agent.py
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from src.state.graph_state import AgentState

class BaseAgent:
    def __init__(self, name: str, llm: BaseChatModel, tools: list[BaseTool], system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        # 如果有工具，则绑定工具给大模型
        self.llm = llm.bind_tools(tools) if tools else llm

    def __call__(self, state: AgentState):
        """这将被作为 LangGraph 的 Node 运行"""
        messages = state.get("messages", [])
        
        # 在消息列表前插入该 Agent 的专属 System Prompt
        if self.system_prompt:
            messages = [SystemMessage(content=self.system_prompt)] + list(messages)
            
        # 调用大模型
        response = self.llm.invoke(messages)
        
        # 返回更新后的状态
        return {
            "messages": [response], 
            "sender": self.name
        }