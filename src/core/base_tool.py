from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Any

# Input schemas for standardizing tool signatures
class CustomToolInput(BaseModel):
    query: str = Field(description="需要处理的具体指令或文本")

class ScoringInput(BaseModel):
    text: str = Field(description="The text to extract score from")

class PrivacyInput(BaseModel):
    score: float = Field(description="The score to encrypt")

class CustomBaseTool(BaseTool):
    name: str = "custom_tool_name"
    description: str = "详细描述这个工具的作用，LLM 会根据这个描述来决定是否调用"
    args_schema: Type[BaseModel] = CustomToolInput

    def _run(self, *args: Any, **kwargs: Any) -> str:
        # 子类应当根据 args_schema 实现具体的 _run 逻辑
        raise NotImplementedError("子类必须实现 _run 方法")
