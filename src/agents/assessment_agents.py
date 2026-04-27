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
