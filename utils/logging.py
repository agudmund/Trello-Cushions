# utils/logging.py
import logging
import logging.handlers
import os
from datetime import datetime
import functools
import time
from typing import Optional


class AppLogger:
    _instance: Optional['AppLogger'] = None
    _logger: logging.Logger = None

    @classmethod
    def get(cls) -> 'AppLogger':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if AppLogger._logger is not None:
            return  # already configured

        self.root_logger = logging.getLogger("trello_cushions")
        self.debug_mode = os.getenv("COZY_DEBUG", "0") == "1"
        self.root_logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)

        # Avoid duplicate handlers
        if self.root_logger.handlers:
            return

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        console.setFormatter(formatter)
        self.root_logger.addHandler(console)

        # Daily file
        log_dir = self._get_log_dir()
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = os.path.join(log_dir, f"trello_log_{today}.txt")

        file_handler = logging.FileHandler(filepath, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        file_handler.setFormatter(formatter)
        self.root_logger.addHandler(file_handler)

    def _get_log_dir(self) -> str:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(root, "logs")
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    def get_today_log_path(self) -> str:
        log_dir = self._get_log_dir()
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(log_dir, f"trello_log_{today}.txt")

    # ── Convenience methods ────────────────────────────────────────

    def debug(self, msg: str, *args, **kwargs) -> None:
        self.root_logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self.root_logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self.root_logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self.root_logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self.root_logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log current exception with traceback."""
        self.root_logger.exception(msg, *args, **kwargs)


# Compatibility / transition helper
def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = AppLogger.get()
        fname = func.__name__
        arg_str = ", ".join(
            [f"{a!r}" for a in args[1:]] +
            [f"{k}={v!r}" for k, v in kwargs.items()]
        )
        logger.debug(f"Calling {fname}({arg_str})")

        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.debug(f"{fname} → {result!r}  ({duration:.3f}s)")
            return result
        except Exception:
            duration = time.time() - start
            logger.exception(f"{fname} raised after {duration:.3f}s")
            raise
    return wrapper


# One-time setup helper (used in main.py)
def setup_logging() -> logging.Logger:
    # Force initialization
    AppLogger.get()
    return logging.getLogger("trello_cushions")