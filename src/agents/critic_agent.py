import json
from .base_agent import BaseAgent
from src.data.prompts import CRITIC_SYSTEM_PROMPT
from src.core.utils import performance_timer

class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Critic")

    @performance_timer
    def run(self, source_text: str, draft_translation: str, context: dict) -> dict:
        """
        Executes the critique task.
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

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if parsing fails
            return {"score": 5, "critique": "Error parsing critic output", "suggestions": "None"}
