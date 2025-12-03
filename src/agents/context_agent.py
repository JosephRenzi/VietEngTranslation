import json
from .base_agent import BaseAgent
from src.data.prompts import CONTEXT_SYSTEM_PROMPT
from src.core.utils import performance_timer

class ContextAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Context")

    @performance_timer
    def run(self, user_input: str, history: list, current_context: dict) -> dict:
        """
        Analyzes input and returns a dictionary of UPDATED context fields.
        """
        
        # Prepare the History string (last 5 turns)
        recent_history = "\n".join(history[-5:]) if history else "No previous conversation."

        # 2. Build the Prompt
        user_prompt = f"""
        USER INPUT: "{user_input}"
        
        RECENT HISTORY:
        {recent_history}
        
        CURRENT CONTEXT STATE:
        {json.dumps(current_context, indent=2)}
        """

        # 3. Define the Schema
        schema = {
            "type": "OBJECT",
            "properties": {
                "reasoning": {"type": "STRING"},
                "updates": {
                    "type": "OBJECT",
                    "properties": {
                        "Speaker_Name": {"type": "STRING"},
                        "Speaker_Gender": {"type": "STRING"},
                        "Audience_Name": {"type": "STRING"},
                        "Audience_Gender": {"type": "STRING"},
                        "Tone": {"type": "STRING"},
                        "Relationship": {"type": "STRING"},
                        "Taboo_Behavior": {"type": "STRING"},
                        "Taboo_Phrases": {"type": "STRING"}
                    }
                }
            },
            "required": ["reasoning", "updates"]
        }

        # 4. Call the LLM
        response_text = self.call_llm(
            system_prompt=CONTEXT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_schema=schema
        )

        if not response_text:
            return {"reasoning": "Error", "updates": {}}

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"reasoning": "Parse Error", "updates": {}}
