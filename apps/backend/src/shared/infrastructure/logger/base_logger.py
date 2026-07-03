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
        self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)

    def exception(self, *args, **kwargs):
        self.logger.exception(*args, **kwargs)

    def success(self, *args, **kwargs):
        self.logger.log(SUCCESS_LEVEL, *args, **kwargs)


@lru_cache
def get_base_logger() -> Logger:
    """
    get base logger
    """
    return Logger()
