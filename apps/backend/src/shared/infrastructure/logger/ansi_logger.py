import logging
import os
import sys
from datetime import UTC, datetime
from json import dumps
from pathlib import Path
from typing import Any

SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(record, "request_id", "-")
        return True


class ColorFormatter(logging.Formatter):
    """
    Color formatter for logger with support for custom levels
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[34m",  # Blue
        "SUCCESS": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


class JsonFormatter(logging.Formatter):
    """Formatter for newline-delimited JSON logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "request_id": getattr(record, "request_id", "-"),
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return dumps(payload, ensure_ascii=True)


def get_logger(name: str):
    """
    Returns an instance of logger with custom level support
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        request_id_filter = RequestIdFilter()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.addFilter(request_id_filter)
        console_formatter = ColorFormatter(
            "%(asctime)s [request_id=%(request_id)s] - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        file_path = Path(os.getenv("LOG_FILE_PATH", "logs/app.log"))
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.addFilter(request_id_filter)
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
