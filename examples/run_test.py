# examples/run_test.py
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
except ImportError:
    # 手动加载 .env 文件
    env_file = project_root / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # 移除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value

from src.workflows.main_graph import app
from langchain_core.messages import HumanMessage
from src.state.graph_state import AgentState

def main():
    print("🤖 欢迎使用多智能体平台 (已接入 LangSmith 监控)")
    user_input = "请查一下关于LangGraph最新的多智能体架构建议，并总结给我。"
    
    # 初始化状态
    initial_state = {"messages": [HumanMessage(content=user_input)]}
    
    # 运行工作流并流式打印
    for output in app.stream(initial_state, stream_mode="updates"):
        for node_name, state_update in output.items():
            print(f"\n--- 更新节点: {node_name} ---")
            if "messages" in state_update:
                latest_msg = state_update["messages"][-1]
                print(f"内容: {latest_msg.content}")

if __name__ == "__main__":
    main()