from functools import lru_cache

from src.core.config.settings import config
from src.shared.infrastructure.logger.ansi_logger import SUCCESS_LEVEL, get_logger


class Logger:
    """
    global logger class with support for custom levels (INFO, SUCCESS, WARNING, ERROR)
    """

    def __init__(self):
        self.logger = get_logger(config.PROJECT_NAME)

    def debug(self, *args, **kwargs):
        """
        Logs a debug message (verbose, expected control flow).
        """
        self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        """
        Logs an informational message.
        """
        self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        """
        Logs a warning message.
        """
        self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        """
        Logs an error message.
        """
        self.logger.error(*args, **kwargs)

    def exception(self, *args, **kwargs):
        """
        Logs an exception message along with the stack trace.
        """
        self.logger.exception(*args, **kwargs)

    def success(self, *args, **kwargs):
        """
        Logs a success message (displayed in green).
        """
        self.logger.log(SUCCESS_LEVEL, *args, **kwargs)


@lru_cache
def get_base_logger() -> Logger:
    """
    get base logger
    """
    return Logger()
