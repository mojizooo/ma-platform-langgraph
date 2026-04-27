from typing import TypedDict, Annotated, Sequence, Any
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    academic_data: dict
    financial_data: dict
    psychological_data: dict
    enc_academic_b64: str
    enc_financial_b64: str
    enc_psych_b64: str
    enc_total_b64: str
    final_alert: bool
    sender: str
