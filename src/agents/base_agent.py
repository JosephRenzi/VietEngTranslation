from abc import ABC, abstractmethod
from google import genai
from google.genai import types
from src.core.config import Config
from src.core.logger import logger
from src.core.utils import performance_timer

class BaseAgent(ABC):
    def __init__(self, name: str, model_name: str = None):
        self.name = name
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        # Default to Translator model if not specified
        self.model = model_name if model_name else Config.TRANSLATOR_MODEL

    @performance_timer
    def call_llm(self, system_prompt: str, user_prompt: str, response_schema=None):
        """
        Wrapper for the Google GenAI call with error handling and logging.
        """
        try:
            config_args = {
                "temperature": 0.7,
            }
            
            if response_schema:
                config_args["response_mime_type"] = "application/json"
                config_args["response_schema"] = response_schema

            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    **config_args
                )
            )

            result_text = response.text
            
            logger.log(
                agent_name=self.name,
                prompt=user_prompt[:200] + "...", 
                output=result_text
            )
            
            return result_text

        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return None
