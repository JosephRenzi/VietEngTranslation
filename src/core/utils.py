import time
from functools import wraps
from colorama import Fore, Style

def performance_timer(func):
    """
    Times execution of a function and prints the duration to the console.
    Uses colorama to distinguish system logs from agent output.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Visual indicator that something is happening in the background
        print(f"{Fore.CYAN}[Timer] Starting: {func.__name__}...{Style.RESET_ALL}")
        
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Print duration with high precision
        print(f"{Fore.CYAN}[Timer] Finished: {func.__name__} in {duration:.4f}s{Style.RESET_ALL}")
        return result
    return wrapper
