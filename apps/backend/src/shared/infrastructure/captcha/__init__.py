from .base_captcha_service import BaseCaptchaService

captcha = BaseCaptchaService("turnstile").client

__all__ = ["captcha"]
