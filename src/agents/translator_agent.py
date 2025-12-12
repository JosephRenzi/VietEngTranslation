import json
from google.genai import types
from .base_agent import BaseAgent
from src.data.prompts import TRANSLATOR_SYSTEM_PROMPT
from src.core.utils import performance_timer
from src.tools.lexicon import lexicon

class TranslatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Translator")

    @performance_timer
    def run(self, source_text: str, context: dict, previous_critique: str = None) -> dict:
        """
        Executes the translation task.
        """
        
        # Simple string matching to find relevant glossary terms
        glossary_hits = []
        # Check if source text contains any keys from our common phrases
        # Note: Your current lexicon is Viet->Eng keys. If translating Eng->Viet, 
        # you need a reverse lookup or a bidirectional dictionary.
        for term, definition in lexicon.common_phrases.items():
            if term in source_text.lower():
                glossary_hits.append(f"{term}: {definition}")
        
        glossary_section = ""
        if glossary_hits:
            glossary_section = "### GLOSSARY (MANDATORY USE):\n" + "\n".join(glossary_hits)
        # -------------------------------------

        user_prompt = f"""
        SOURCE TEXT: "{source_text}"
        
        {glossary_section}  <-- INJECT HERE
        
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
