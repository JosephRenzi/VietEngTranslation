import json
from google.genai import types
from .base_agent import BaseAgent
from src.data.prompts import TRANSLATOR_SYSTEM_PROMPT
from src.core.utils import performance_timer

class TranslatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Translator")

    @performance_timer
    def run(self, source_text: str, context: dict, previous_critique: str = None) -> dict:
        """
        Executes the translation task.
        """
        
        # 1. Build the User Prompt
        user_prompt = f"""
        SOURCE TEXT: "{source_text}"
        
        CONTEXT PROFILE:
        {json.dumps(context, indent=2)}
        """

        if previous_critique:
            user_prompt += f"\n\nPREVIOUS CRITIQUE (FIX THESE ERRORS):\n{previous_critique}"

        # 2. Define Output Schema for Structured Output
        # Gemini 2.0 supports Pydantic-like schemas or raw dictionaries
        schema = {
            "type": "OBJECT",
            "properties": {
                "translation": {"type": "STRING"},
                "reasoning": {"type": "STRING"}
            },
            "required": ["translation", "reasoning"]
        }

        # 3. Call LLM
        response_text = self.call_llm(
            system_prompt=TRANSLATOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_schema=schema
        )

        # 4. Parse JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"translation": response_text, "reasoning": "Parsing Error"}
