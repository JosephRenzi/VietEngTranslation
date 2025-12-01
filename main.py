import sys
import os
import json
from colorama import Fore, Style 

from src.core.config import Config
from src.core.reflection_loop import ReflectionLoop
from src.core.utils import performance_timer
from src.data.defaults import DEFAULT_CONTEXT
from src.agents.context_agent import ContextAgent

# Ensure we can import from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def swap_roles(ctx):
    """
    Helper to flip Speaker/Audience profiles and Languages.
    """
    ctx["Source_Language"], ctx["Target_Language"] = ctx["Target_Language"], ctx["Source_Language"]
    
    keys = list(ctx.keys())
    for key in keys:
        if key.startswith("Speaker_"):
            audience_key = "Audience_" + key.split("Speaker_")[1]
            if audience_key in ctx:
                ctx[key], ctx[audience_key] = ctx[audience_key], ctx[key]

    print(f"\n{Fore.CYAN}[System] Swapped Roles: Now translating {ctx['Source_Language']} -> {ctx['Target_Language']}{Style.RESET_ALL}")
    return ctx

@performance_timer
def main():
    print("Initializing Text-Only Translation System...")
    
    try:
        Config.validate()
    except Exception as e:
        print(f"Error: {e}")
        return

    # 1. Initialize State
    context = DEFAULT_CONTEXT.copy()
    chat_history = [] 
    
    # 2. Initialize Agents
    loop = ReflectionLoop()
    context_agent = ContextAgent()

    print("-" * 50)
    print(f" SYSTEM READY (Critic: {Config.CRITIC_MODEL}) ")
    print("-" * 50)
    
    while True:
        direction_label = f"{context.get('Source_Language', '???')}->{context.get('Target_Language', '???')}"
        mode = input(f"\n[{direction_label}] [T]ype, [S]wap, [C]ontext, [Q]uit? ").upper().strip()
        
        if mode == "Q":
            break  
        elif mode == "C":
            print(json.dumps(context, indent=2))
            continue
        elif mode == "S":
            context = swap_roles(context)
            continue
            
        source_text = ""
        
        if mode == "T":
            source_text = input("Enter text: ")

        if source_text:
            # Step A: Context Inference
            print(f"\n{Fore.CYAN}>> Analyzing Context...{Style.RESET_ALL}")
            analysis = context_agent.run(source_text, chat_history, context)
            
            updates = analysis.get("updates", {})
            reasoning = analysis.get("reasoning", "")

            if updates:
                print(f"{Fore.MAGENTA}[Context Update]: {json.dumps(updates, indent=2)}{Style.RESET_ALL}")
                print(f"{Style.DIM}Reasoning: {reasoning}{Style.RESET_ALL}")
                context.update(updates)
            else:
                print(f"{Style.DIM}No context changes detected.{Style.RESET_ALL}")

            # Step B: Translation (Reflection Loop)
            result = loop.process_request(source_text, context)
            final_translation = result.get('final_translation')
            
            print("\n" + "="*30)
            print(f"FINAL: {final_translation}")
            print("="*30)

            # Step C: Update History
            chat_history.append(f"User: {source_text}")
            chat_history.append(f"Translator: {final_translation}")

if __name__ == "__main__":
    main()
