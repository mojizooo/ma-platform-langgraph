import re
from src.core.base_tool import CustomBaseTool, ScoringInput

class ScoringTool(CustomBaseTool):
    name: str = "scoring_tool"
    description: str = "Extracts a numerical score (0-100) from text."
    args_schema = ScoringInput
    
    def _run(self, text: str) -> float:
        match = re.search(r"[-+]?\d*\.\d+|\d+", text)
        return float(match.group()) if match else 0.0
