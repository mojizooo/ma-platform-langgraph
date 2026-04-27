# Parallel Privacy-Preserving Multi-Agent Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the student crisis assessment into a modular, parallel LangGraph workflow using TenSEAL for privacy-preserving score aggregation.

**Architecture:** A fan-out/fan-in graph where three specialized agents (Academic, Financial, Psychological) perform assessments in parallel, producing encrypted scores. A Coordinator agent aggregates these scores homomorphically before an Oracle decrypts the final result.

**Tech Stack:** Python, LangGraph, TenSEAL, LangChain (OpenAI/Qwen).

---

### Task 1: Refine Core and State

**Files:**
- Modify: `src/state/graph_state.py`
- Modify: `src/core/base_agent.py`
- Modify: `src/core/base_tool.py`

- [ ] **Step 1: Update AgentState**
Update `AgentState` to include all necessary fields for parallel assessment and message history.

```python
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
```

- [ ] **Step 2: Standardize BaseTool**
Ensure `BaseTool` has a clear `_run` signature.

```python
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class ScoringInput(BaseModel):
    text: str = Field(description="The text to extract score from")

class PrivacyInput(BaseModel):
    score: float = Field(description="The score to encrypt")
```

- [ ] **Step 3: Commit Core Changes**
```bash
git add src/state/graph_state.py src/core/base_agent.py src/core/base_tool.py
git commit -m "refactor: update state and core base classes"
```

---

### Task 2: Implement Utilities and Tools

**Files:**
- Create: `src/utils/key_manager.py`
- Create: `src/tools/scoring_tool.py`
- Create: `src/tools/privacy_tool.py`

- [ ] **Step 1: Implement KeyManager**
Create a utility to handle TenSEAL context serialization/deserialization.

```python
import os
import tenseal as ts

SECRET_KEY_PATH = os.path.join(os.path.dirname(__file__), '../workflows/secret_context.bytes')
PUBLIC_KEY_PATH = os.path.join(os.path.dirname(__file__), '../workflows/public_context.bytes')

class KeyManager:
    @staticmethod
    def get_context(is_private: bool = False):
        path = SECRET_KEY_PATH if is_private else PUBLIC_KEY_PATH
        if not os.path.exists(path):
            context = ts.context(ts.SCHEME_TYPE.CKKS, 8192, [60, 40, 40, 60])
            context.global_scale = 2**40
            context.generate_galois_keys()
            with open(SECRET_KEY_PATH, 'wb') as f: f.write(context.serialize(save_secret_key=True))
            context.make_context_public()
            with open(PUBLIC_KEY_PATH, 'wb') as f: f.write(context.serialize())
            return context if is_private else context
        with open(path, 'rb') as f: return ts.context_from(f.read())
```

- [ ] **Step 2: Implement ScoringTool**
```python
import re
from src.core.base_tool import CustomBaseTool

class ScoringTool(CustomBaseTool):
    name: str = "scoring_tool"
    description: str = "Extracts a numerical score (0-100) from text."
    
    def _run(self, text: str) -> float:
        match = re.search(r"[-+]?\d*\.\d+|\d+", text)
        return float(match.group()) if match else 0.0
```

- [ ] **Step 3: Implement PrivacyTool**
```python
import base64
import tenseal as ts
from src.utils.key_manager import KeyManager

class PrivacyTool:
    @staticmethod
    def encrypt(score: float) -> str:
        context = KeyManager.get_context(is_private=False)
        enc_vec = ts.ckks_vector(context, [score])
        return base64.b64encode(enc_vec.serialize()).decode('utf-8')

    @staticmethod
    def decrypt(b64_str: str) -> float:
        context = KeyManager.get_context(is_private=True)
        enc_vec = ts.ckks_vector_from(context, base64.b64decode(b64_str.encode('utf-8')))
        return enc_vec.decrypt()[0]
```

- [ ] **Step 4: Commit Tools**
```bash
git add src/utils/key_manager.py src/tools/scoring_tool.py src/tools/privacy_tool.py
git commit -m "feat: add key manager and privacy tools"
```

---

### Task 3: Implement Specialized Agents

**Files:**
- Create: `src/agents/assessment_agents.py`
- Create: `src/agents/coordinator_agent.py`

- [ ] **Step 1: Assessment Agents**
Implement `AcademicAgent`, `FinancialAgent`, and `PsychologicalAgent` in `src/agents/assessment_agents.py`.

```python
import json
from src.core.base_agent import BaseAgent
from src.tools.scoring_tool import ScoringTool
from src.tools.privacy_tool import PrivacyTool
from langchain_core.messages import HumanMessage

class AssessmentAgent(BaseAgent):
    def __init__(self, name: str, domain: str, llm):
        system_prompt = f"你是一个{domain}危机评估智能体。根据数据打分 (0-100)。只返回纯数字。"
        super().__init__(name, llm, [], system_prompt)
        self.domain = domain
        self.scoring_tool = ScoringTool()

    def __call__(self, state):
        data_key = f"{self.name.split('_')[0]}_data"
        data = state.get(data_key, {})
        prompt = f"{self.domain}数据：{json.dumps(data)}"
        response = self.llm.invoke([HumanMessage(content=prompt)])
        score = self.scoring_tool._run(response.content)
        enc_b64 = PrivacyTool.encrypt(max(0.0, min(100.0, score)))
        return {f"enc_{self.name.split('_')[0]}_b64": enc_b64, data_key: {}}
```

- [ ] **Step 2: Coordinator Agent**
```python
import base64
import tenseal as ts
from src.utils.key_manager import KeyManager

def coordinator_agent(state):
    context = KeyManager.get_context(is_private=False)
    def decode(b64): return ts.ckks_vector_from(context, base64.b64decode(b64.encode('utf-8'))) if b64 else ts.ckks_vector(context, [0.0])
    
    a_vec = decode(state.get("enc_academic_b64"))
    f_vec = decode(state.get("enc_financial_b64"))
    p_vec = decode(state.get("enc_psych_b64"))
    
    total = a_vec * 0.4 + f_vec * 0.3 + p_vec * 0.3
    return {"enc_total_b64": base64.b64encode(total.serialize()).decode('utf-8')}
```

- [ ] **Step 3: Commit Agents**
```bash
git add src/agents/assessment_agents.py src/agents/coordinator_agent.py
git commit -m "feat: implement assessment and coordinator agents"
```

---

### Task 4: Orchestrate Parallel Graph

**Files:**
- Modify: `src/workflows/main_graph.py`

- [ ] **Step 1: Refactor main_graph.py**
Assemble the nodes into a parallel graph.

```python
from langgraph.graph import StateGraph, START, END
from src.state.graph_state import AgentState
from src.agents.assessment_agents import AssessmentAgent
from src.agents.coordinator_agent import coordinator_agent
from src.tools.privacy_tool import PrivacyTool
from src.utils.key_manager import KeyManager

# Nodes
def key_node(state):
    KeyManager.get_context(is_private=True) # Ensure keys exist
    return {"academic_data": state["raw_data"]["academic_data"], ...} # split data

def oracle_node(state):
    score = PrivacyTool.decrypt(state["enc_total_b64"])
    return {"final_alert": score > 75.0}

workflow = StateGraph(AgentState)
workflow.add_node("key_management", key_node)
workflow.add_node("academic", AssessmentAgent("academic", "学业", llm))
workflow.add_node("financial", AssessmentAgent("financial", "财务", llm))
workflow.add_node("psychological", AssessmentAgent("psychological", "心理", llm))
workflow.add_node("coordinator", coordinator_agent)
workflow.add_node("oracle", oracle_node)

workflow.add_edge(START, "key_management")
workflow.add_edge("key_management", "academic")
workflow.add_edge("key_management", "financial")
workflow.add_edge("key_management", "psychological")
workflow.add_edge("academic", "coordinator")
workflow.add_edge("financial", "coordinator")
workflow.add_edge("psychological", "coordinator")
workflow.add_edge("coordinator", "oracle")
workflow.add_edge("oracle", END)
```

- [ ] **Step 2: Verify with Tests**
Run `python examples/test_privacy_workflow.py` and ensure it passes.

- [ ] **Step 3: Commit and Finish**
```bash
git add src/workflows/main_graph.py
git commit -m "feat: orchestrate parallel assessment graph"
```
