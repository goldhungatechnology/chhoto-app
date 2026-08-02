from src.core.config.settings import config

from .base_captcha_service import BaseCaptchaService

captcha = BaseCaptchaService(config.CAPTCHA_PROVIDER).client

__all__ = ["captcha"]
