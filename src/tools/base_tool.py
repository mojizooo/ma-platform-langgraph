# src/core/base_tool.py
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# 提供一个标准模板供大家参考
class CustomToolInput(BaseModel):
    query: str = Field(description="需要处理的具体指令或文本")

class CustomBaseTool(BaseTool):
    name: str = "custom_tool_name"
    description: str = "详细描述这个工具的作用，LLM 会根据这个描述来决定是否调用"
    args_schema: Type[BaseModel] = CustomToolInput

    def _run(self, query: str) -> str:
        # 这里让其他同学填入他们自己的业务逻辑（例如调用外部API、跑一段模型推理等）
        raise NotImplementedError("子类必须实现 _run 方法")