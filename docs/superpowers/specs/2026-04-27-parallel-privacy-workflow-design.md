# Parallel Privacy-Preserving Multi-Agent Workflow Design

## 1. Overview
This design expands the `ma-platform-langgraph` framework into a modular, parallel-execution system for student crisis assessment. It leverages LangGraph for orchestration and TenSEAL (CKKS) for privacy-preserving computations on sensitive risk scores.

## 2. Architecture

### 2.1 Component Diagram (Logical)
```
[START] -> [KeyManagementNode] 
              |
      ---------------------------------
      |               |               |
[AcademicAgent] [FinancialAgent] [PsychologicalAgent]
      |               |               |
      ---------------------------------
              |
      [CoordinatorAgent] -> [OracleNode] -> [END]
```

### 2.2 Directory Structure
- `src/agents/`: Concrete implementations of `AcademicAgent`, `FinancialAgent`, `PsychologicalAgent`, and `CoordinatorAgent`.
- `src/tools/`: `PrivacyTool` (encryption/decryption) and `ScoringTool` (regex extraction).
- `src/core/`: `BaseAgent` for common agent behaviors and `BaseTool` for standardizing tools.
- `src/state/`: `AgentState` definition with support for parallel updates and message history.
- `src/workflows/`: `main_graph.py` as the clean orchestrator.
- `src/utils/`: `key_manager.py` for TenSEAL context persistence and `logger.py` for system tracing.

## 3. Detailed Component Specs

### 3.1 Agents
- **Assessment Agents (Academic, Financial, Psychological)**:
    - Inherit from `BaseAgent`.
    - Use a system prompt specialized for their domain.
    - Output: An encrypted CKKS vector (Base64) stored in the state.
- **Coordinator Agent**:
    - Aggregates the three encrypted vectors using weighted averaging (`0.4 * Academic + 0.3 * Financial + 0.3 * Psych`).
    - Operates entirely on encrypted data (public context).

### 3.2 Tools
- **PrivacyTool**:
    - `encrypt(score: float, context: ts.Context) -> str (b64)`
    - `decrypt(b64_str: str, secret_context: ts.Context) -> float`
- **ScoringTool**:
    - `extract_score(text: str) -> float` (Standardized regex parser).

### 3.3 State Management
The `AgentState` will be defined as:
```python
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
```

## 4. Execution Flow
1. **Init**: `KeyManagementNode` ensures TenSEAL contexts exist.
2. **Parallel Fan-out**: `AcademicAgent`, `FinancialAgent`, and `PsychologicalAgent` run concurrently.
3. **Fan-in**: `CoordinatorAgent` waits for all three encrypted strings to be present in the state.
4. **Aggregation**: `CoordinatorAgent` performs homomorphic addition/multiplication.
5. **Decryption**: `OracleNode` uses the secret key to decrypt the final result and set `final_alert`.

## 5. Testing Strategy
- **Unit Tests**: Test `PrivacyTool` for encryption/decryption consistency.
- **Integration Tests**: Verify the parallel branches correctly update the state without collisions.
- **End-to-End**: Run `test_privacy_workflow.py` to ensure the final assessment matches expected outcomes for mock students.
