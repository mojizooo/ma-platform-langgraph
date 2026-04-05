#!/usr/bin/env python
"""项目执行脚本 - 从根目录运行"""
import sys
import os
from pathlib import Path

# 确保项目根目录在 Python 路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量文件位置
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

# 导入并运行测试
from examples.run_test import main

if __name__ == "__main__":
    main()
