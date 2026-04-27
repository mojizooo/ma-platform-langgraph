import os
import tenseal as ts
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from src.state.graph_state import AgentState
from src.agents.assessment_agents import AssessmentAgent
from src.agents.coordinator_agent import coordinator_agent
from src.tools.privacy_tool import PrivacyTool
from src.utils.key_manager import KeyManager

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# LLM Initialization
llm = ChatOpenAI(
    model=os.getenv("QWEN_MODEL"),
    api_key=os.getenv("QWEN_API_KEY"),
    base_url=os.getenv("QWEN_API_BASE"),
    temperature=0
)

# Nodes
def key_management_node(state):
    KeyManager.get_context(is_private=True) # Ensure keys exist
    raw_data = state.get("raw_data", {})
    return {
        "academic_data": raw_data.get("academic_data", {}),
        "financial_data": raw_data.get("financial_data", {}),
        "psychological_data": raw_data.get("psychological_data", {}),
        "raw_data": {} 
    }

def oracle_node(state):
    enc_total_b64 = state.get("enc_total_b64")
    if not enc_total_b64:
        return {"final_alert": False}
    score = PrivacyTool.decrypt(enc_total_b64)
    return {"final_alert": bool(score > 75.0)}

# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("key_management", key_management_node)
workflow.add_node("academic", AssessmentAgent("academic_agent", "学业", llm))
workflow.add_node("financial", AssessmentAgent("financial_agent", "财务", llm))
workflow.add_node("psychological", AssessmentAgent("psych_agent", "心理", llm))
workflow.add_node("coordinator", coordinator_agent)
workflow.add_node("oracle", oracle_node)

workflow.add_edge(START, "key_management")
# Parallel fan-out
workflow.add_edge("key_management", "academic")
workflow.add_edge("key_management", "financial")
workflow.add_edge("key_management", "psychological")
# Fan-in to coordinator
workflow.add_edge("academic", "coordinator")
workflow.add_edge("financial", "coordinator")
workflow.add_edge("psychological", "coordinator")

workflow.add_edge("coordinator", "oracle")
workflow.add_edge("oracle", END)

app = workflow.compile()
