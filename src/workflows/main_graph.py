import json
import os
import base64
import re
import logging
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# 使用 Qwen 模型
llm = ChatOpenAI(
    model=os.getenv("QWEN_MODEL"),
    api_key=os.getenv("QWEN_API_KEY"),
    base_url=os.getenv("QWEN_API_BASE"),
    temperature=0
)

def extract_float_from_content(content: str) -> float:
    match = re.search(r"[-+]?\d*\.\d+|\d+", content)
    if match:
        try:
            return float(match.group())
        except:
            return 0.0
    return 0.0

try:
    import tenseal as ts
except ImportError:
    print("Warning: tenseal is not installed. Please run 'pip install tenseal'")
    ts = None

# 本地密钥文件约定
SECRET_KEY_PATH = os.path.join(os.path.dirname(__file__), 'secret_context.bytes')
PUBLIC_KEY_PATH = os.path.join(os.path.dirname(__file__), 'public_context.bytes')

# ============== 1. State 定义 ==============
class AgentState(TypedDict, total=False):
    student_id: str
    raw_data: dict
    academic_data: dict
    financial_data: dict
    psychological_data: dict
    enc_academic_b64: str
    enc_financial_b64: str
    enc_psych_b64: str
    enc_total_b64: str
    final_alert: bool

# ============== 2. Node 函数编写 ==============
def key_management_node(state: AgentState):
    raw_data = state.get("raw_data", {})
    
    updates = {
        "raw_data": {},
        "academic_data": raw_data.get("academic_data", {}),
        "financial_data": raw_data.get("financial_data", {}),
        "psychological_data": raw_data.get("psychological_data", {})
    }

    if ts is None:
        raise ImportError("tenseal is missing")
        
    if os.path.exists(SECRET_KEY_PATH) and os.path.exists(PUBLIC_KEY_PATH):
        return updates

    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.global_scale = 2**40
    context.generate_galois_keys()

    with open(SECRET_KEY_PATH, 'wb') as f:
        f.write(context.serialize(save_secret_key=True))

    context.make_context_public()
    
    with open(PUBLIC_KEY_PATH, 'wb') as f:
        f.write(context.serialize())

    return updates

def _get_public_context():
    with open(PUBLIC_KEY_PATH, 'rb') as f:
        context_bytes = f.read()
    return ts.context_from(context_bytes)

def academic_agent(state: AgentState):
    context = _get_public_context()
    academic_data = state.get("academic_data", {})
    
    prompt = f"""你是一个学业危机评估智能体。
请根据以下学生的学业数据综合打分，生成一个 0 到 100 之间的浮点数作为“学业风险分”。
分数越高代表学业危机越大（例如 GPA 极低、挂科数多则风险分高）。
不要输出任何其他文本和解释，只需要返回纯数字。

学业数据：
{json.dumps(academic_data, ensure_ascii=False)}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    academic_score = extract_float_from_content(response.content)
    
    academic_score = max(0.0, min(100.0, academic_score))
    
    enc_vec = ts.ckks_vector(context, [academic_score])
    enc_b64 = base64.b64encode(enc_vec.serialize()).decode('utf-8')
    
    return {"enc_academic_b64": enc_b64, "academic_data": {}}

def financial_agent(state: AgentState):
    context = _get_public_context()
    financial_data = state.get("financial_data", {})
    
    prompt = f"""你是一个财务危机评估智能体。
请根据以下学生的财务数据综合打分，生成一个 0 到 100 之间的浮点数作为“财务风险分”。
分数越高代表财务危机越大（例如生活费极低、负债高等）。
不要输出任何其他文本和解释，只需要返回纯数字。

财务数据：
{json.dumps(financial_data, ensure_ascii=False)}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    financial_score = extract_float_from_content(response.content)
    
    financial_score = max(0.0, min(100.0, financial_score))
    
    enc_vec = ts.ckks_vector(context, [financial_score])
    enc_b64 = base64.b64encode(enc_vec.serialize()).decode('utf-8')
    
    return {"enc_financial_b64": enc_b64, "financial_data": {}}

def psychological_agent(state: AgentState):
    context = _get_public_context()
    psychological_data = state.get("psychological_data", {})
    
    prompt = f"""你是一个心理危机评估智能体。
请根据以下学生的心理数据综合打分，生成一个 0 到 100 之间的浮点数作为“心理风险分”。
分数越高代表心理危机越大（例如压力指数高、睡眠质量差等）。
不要输出任何其他文本和解释，只需要返回纯数字。

心理数据：
{json.dumps(psychological_data, ensure_ascii=False)}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    psych_score = extract_float_from_content(response.content)
    
    psych_score = max(0.0, min(100.0, psych_score))
    
    enc_vec = ts.ckks_vector(context, [psych_score])
    enc_b64 = base64.b64encode(enc_vec.serialize()).decode('utf-8')
    
    return {"enc_psych_b64": enc_b64, "psychological_data": {}}

def coordinator_agent(state: AgentState):
    context = _get_public_context()
    
    def decode_vec(b64_str: str):
        if not b64_str:
            return ts.ckks_vector(context, [0.0])
        return ts.ckks_vector_from(context, base64.b64decode(b64_str.encode('utf-8')))
        
    academic_vec = decode_vec(state.get("enc_academic_b64", ""))
    financial_vec = decode_vec(state.get("enc_financial_b64", ""))
    psych_vec = decode_vec(state.get("enc_psych_b64", ""))
    
    total_vec = academic_vec * 0.4 + financial_vec * 0.3 + psych_vec * 0.3
    
    enc_total_b64 = base64.b64encode(total_vec.serialize()).decode('utf-8')
    return {"enc_total_b64": enc_total_b64}

def oracle_node(state: AgentState):
    with open(SECRET_KEY_PATH, 'rb') as f:
        secret_context_bytes = f.read()
    secret_context = ts.context_from(secret_context_bytes)
    
    enc_total_b64 = state.get("enc_total_b64")
    total_vec = ts.ckks_vector_from(secret_context, base64.b64decode(enc_total_b64.encode('utf-8')))
    
    result_list = total_vec.decrypt()
    total_score = result_list[0] if result_list else 0.0
    
    final_alert = bool(total_score > 75.0)
    
    return {"final_alert": final_alert}

# ============== 3. Graph 编译 ==============
workflow = StateGraph(AgentState)

workflow.add_node("key_management_node", key_management_node)
workflow.add_node("academic_agent", academic_agent)
workflow.add_node("financial_agent", financial_agent)
workflow.add_node("psychological_agent", psychological_agent)
workflow.add_node("coordinator_agent", coordinator_agent)
workflow.add_node("oracle_node", oracle_node)

workflow.add_edge(START, "key_management_node")
workflow.add_edge("key_management_node", "academic_agent")
workflow.add_edge("academic_agent", "financial_agent")
workflow.add_edge("financial_agent", "psychological_agent")
workflow.add_edge("psychological_agent", "coordinator_agent")
workflow.add_edge("coordinator_agent", "oracle_node")
workflow.add_edge("oracle_node", END)

app = workflow.compile()
