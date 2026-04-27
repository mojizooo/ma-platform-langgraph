import re
from typing import Type
from pydantic import BaseModel
from src.core.base_tool import CustomBaseTool, ScoringInput

class ScoringTool(CustomBaseTool):
    name: str = "scoring_tool"
    description: str = "Extracts a numerical score (0-100) from text."
    args_schema: Type[BaseModel] = ScoringInput
    
    def _run(self, text: str) -> float:
        match = re.search(r"[-+]?\d*\.\d+|\d+", text)
        return float(match.group()) if match else 0.0
