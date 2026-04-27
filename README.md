# MA-Platform built on Langgraph

基于 **LangGraph** 和 **TenSEAL** 构建的隐私保护多智能体工作流评估系统。

## 项目简介
演示了在多智能体场景下，通过 **并行工作流** 实现敏感数据的切片隔离与同态加密运算隐私保护。系统以 **学生危机（学业、财务、心理）评估** 为业务场景，各评估智能体在不接触非相关数据的情况下独立给出评分，并由协调智能体在加密状态下完成加权汇总。

## 核心架构
- **并行评估层 (Parallel Assessment)**: `AcademicAgent`、`FinancialAgent`、`PsychAgent` 并行运行，互不干扰。
- **隐私计算层 (Privacy Computing)**: 利用 TenSEAL (CKKS) 实现分数的同态加密。
- **协调层 (Coordination)**: `CoordinatorAgent` 在不解密的情况下，通过同态加法和乘法完成分数的加权聚合。
- **审计层 (Oracle)**: 最终持有私钥的节点对汇总结果进行解密并输出风险预警。

## 项目结构
- `src/agents/`: 具体的评估与协调智能体实现。
- `src/tools/`: 隐私加解密工具与评分提取工具。
- `src/core/`: 智能体与工具的基类定义。
- `src/state/`: 基于 LangGraph 的状态管理。
- `src/workflows/`: 并行工作流图定义。

## 快速开始

### 1. 环境准备
安装相关依赖：
```bash
pip install tenseal langchain_openai langgraph langgraph-checkpoint python-dotenv
```

### 2. 配置环境变量
确保在外层目录（或当前目录）的 `.env` 中配置兼容 OpenAI 格式的模型密钥（当前主要为 Qwen）。
```env
QWEN_MODEL=qwen-max
QWEN_API_KEY=your_api_key_here
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 3. 生成 Mock 数据
在 `ma-platform-langgraph` 目录下执行：
```bash
python examples/generate_crisis_mock_data.py
```
这会在 `examples` 文件夹内生成 `crisis_mock_data.json` 测试基准数据。

### 4. 执行多智能体评估测试
执行以下指令：
```bash
python examples/test_privacy_workflow.py
```

### 5.日志追踪
确保在外层目录（或当前目录）的 `.env` 中配置langgsmith专用api。
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=
```
