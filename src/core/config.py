import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Selection
    # Translator: Fast & Cheap (Optimized for speed)
    TRANSLATOR_MODEL = "gemini-2.0-flash-lite-001" 
    
    # Critic: Strong & Capable (Standard 2.0 Pro)
    CRITIC_MODEL = "gemini-2.0-pro" 
    
    # Thresholds
    CRITIC_SCORE_THRESHOLD = 8
    MAX_RETRIES = 2
    
    # Database
    DB_PATH: str = "translation_logs.db"

    @staticmethod
    def validate():
        """
        Validates the configuration by checking API key existence and validity.
        """
        if not Config.GOOGLE_API_KEY:
            raise ValueError(
                "\n[FATAL] GOOGLE_API_KEY not found in environment.\n"
                "Please create a .env file with GOOGLE_API_KEY='your_key_here'"
            )

        print(f"[System]: Validating API Key: {Config.GOOGLE_API_KEY[:4]}...****")
        try:
            client = genai.Client(
                api_key=Config.GOOGLE_API_KEY, 
                http_options={'api_version': 'v1'}
            )
            list(client.models.list(config={'page_size': 1}))
            print("[System]: Connection successful. API Key is valid.")
            return True
        except Exception as e:
            raise ConnectionError(f"\n[FATAL] API Key Validation Failed: {e}")
