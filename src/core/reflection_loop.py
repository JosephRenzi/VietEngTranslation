from colorama import Fore, Style
from src.agents.translator_agent import TranslatorAgent 
from src.agents.critic_agent import CriticAgent         
from src.core.config import Config
from src.core.utils import performance_timer

class ReflectionLoop:
    def __init__(self):
        self.translator = TranslatorAgent()
        self.critic = CriticAgent()

    @performance_timer
    def process_request(self, source_text: str, context: dict):
        """
        Manages the Reflection Loop:
        1. Translate
        2. Critique
        3. Loop if Score < Threshold
        """
        print(f"\n{Fore.CYAN}--- REFLECTION LOOP STARTED ---{Style.RESET_ALL}")
        
        # [FIX] Initialize as empty string to satisfy 'str' type requirement
        current_critique = ""
        attempt = 1
        
        while attempt <= Config.MAX_RETRIES + 1:
            print(f"\n{Fore.YELLOW}>> Attempt {attempt} (Translator Working...){Style.RESET_ALL}")
            
            # 1. Translate
            draft = self.translator.run(source_text, context, previous_critique=current_critique)
            
            # SAFEGUARD: Ensure we get strings, not None
            translation_text = draft.get("translation") or ""
            reasoning = draft.get("reasoning") or "No reasoning provided"
            
            # FIXED: Use Style.DIM instead of Fore.DIM
            print(f"{Fore.GREEN}Draft:{Style.RESET_ALL} {translation_text}")
            print(f"{Style.DIM}Reasoning: {reasoning}{Style.RESET_ALL}")

            # 2. Critique
            print(f"{Fore.YELLOW}>> (Critic Analyzing...){Style.RESET_ALL}")
            feedback = self.critic.run(source_text, translation_text, context)
            
            # SAFEGUARD: Handle missing keys gracefully
            score = feedback.get("score") # May be None if parsing failed
            critique_text = feedback.get("critique") or "No critique provided"
            
            # Handle the case where score is missing/None (default to 0 to force retry)
            safe_score = score if isinstance(score, int) else 0
            
            print(f"{Fore.BLUE}Score: {safe_score}/10{Style.RESET_ALL}")
            print(f"{Fore.BLUE}Critique: {critique_text}{Style.RESET_ALL}")

            # 3. Decision Logic
            # Check safe_score instead of potentially None score
            if safe_score >= Config.CRITIC_SCORE_THRESHOLD:
                print(f"\n{Fore.CYAN}--- SUCCESS: Quality Threshold Met ---{Style.RESET_ALL}")
                return {
                    "final_translation": translation_text,
                    "final_score": safe_score,
                    "attempts": attempt
                }
            else:
                print(f"{Fore.RED}>> Score too low. Retrying...{Style.RESET_ALL}")
                current_critique = f"Previous draft received score {safe_score}/10. Critique: {critique_text}. Suggestions: {feedback.get('suggestions')}"
                attempt += 1

        print(f"\n{Fore.RED}--- WARNING: Max Retries Exceeded ---{Style.RESET_ALL}")
        return {
            "final_translation": translation_text,
            "final_score": safe_score, # Use the last known safe score
            "note": "Max retries reached. Result may be imperfect."
        }
