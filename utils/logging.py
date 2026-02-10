# utils/logging.py
import os
from datetime import datetime
import functools
import time


def get_log_dir():
    """
    Returns the logs directory relative to project root.
    Creates the folder if it doesn't exist.
    """
    # Up two levels from utils/ to reach project root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(root_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)  # auto-create folder
    return log_dir


def get_log_filename():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(get_log_dir(), f"trello_log_{today}.txt")


def log_message(message: str, level: str = "INFO"):
    """
    Log a message with optional level prefix.
    Levels are visual only (no filtering yet).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = get_log_filename()
    log_line = f"[{timestamp}] [{level}] {message}"
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + "\n")
            f.flush()
            os.fsync(f.fileno())
        print(f"Logged: {log_line}")
    except Exception as e:
        print(f"LOG ERROR: Failed to write to {log_file}: {e}")


def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        arg_str = ", ".join([f"{a!r}" for a in args[1:]] + [f"{k}={v!r}" for k, v in kwargs.items()])
        log_message(f"Calling {func_name}({arg_str})")
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            log_message(f"{func_name} returned {result!r} in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start
            log_message(f"{func_name} raised {type(e).__name__}: {e} after {duration:.3f}s", level="ERROR")
            raise
    return wrapper