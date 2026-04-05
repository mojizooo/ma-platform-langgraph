# src/state/graph_state.py
from typing import TypedDict, Annotated, Sequence, Any
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # 使用 operator.add 确保每次产生新消息时都是追加，而不是覆盖
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # 记录当前是由哪个 Agent 发出的消息，方便做路由跳转
    sender: str 
    
    # 用于存放各 Agent 协同过程中产生的结构化数据（例如解析后的 JSON、提取的反应图节点等）
    shared_memory: dict[str, Any]