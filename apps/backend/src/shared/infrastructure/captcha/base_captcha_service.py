from typing import Literal

from src.shared.infrastructure.captcha.adapter.turnstile.turnstile_captcha_service import (
    TurnstileCaptchaService,
)


class BaseCaptchaService:
    def __init__(self, provider: Literal["turnstile"]):
        match provider:
            case "turnstile":
                self._service = TurnstileCaptchaService()
            case _:
                raise ValueError(f"Unsupported captcha provider: {provider}")

    @property
    def client(self) -> TurnstileCaptchaService:
        return self._service
