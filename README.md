# MA-Platform built on Langgraph

基于**LangGraph**和**TenSEAL**构建的隐私保护多智能体工作流评估系统。

## 项目简介
演示了简单多智能体场景下实现敏感数据的切片隔离与运算隐私保护。以**学生危机（学业、财务、心理）评估**为业务场景。

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
