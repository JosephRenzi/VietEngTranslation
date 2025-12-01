import json
from .base_agent import BaseAgent
from src.data.prompts import CRITIC_SYSTEM_PROMPT
from src.core.utils import performance_timer
from src.core.config import Config

class CriticAgent(BaseAgent):
    def __init__(self):
        # We explicitly ask for the Stronger Model here
        super().__init__(name="Critic", model_name=Config.CRITIC_MODEL)

    @performance_timer
    def run(self, source_text: str, draft_translation: str, context: dict) -> dict:
        """
        Executes the critique task using a stronger reasoning model.
        """
        
        user_prompt = f"""
        SOURCE TEXT: "{source_text}"
        DRAFT TRANSLATION: "{draft_translation}"
        
        CONTEXT PROFILE:
        {json.dumps(context, indent=2)}
        """

        schema = {
            "type": "OBJECT",
            "properties": {
                "score": {"type": "INTEGER"},
                "critique": {"type": "STRING"},
                "suggestions": {"type": "STRING"}
            },
            "required": ["score", "critique", "suggestions"]
        }

        response_text = self.call_llm(
            system_prompt=CRITIC_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_schema=schema
        )

        if not response_text:
            return {"score": 0, "critique": "Error: No response from model", "suggestions": "Check logs"}

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"score": 5, "critique": "Error parsing critic output", "suggestions": "None"}
