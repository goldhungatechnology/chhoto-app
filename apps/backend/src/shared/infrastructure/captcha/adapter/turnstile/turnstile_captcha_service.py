import httpx

from src.core.config.settings import config
from src.shared.infrastructure.captcha.interface.captcha_interface import (
    ICaptchaService,
)
from src.shared.infrastructure.logger import logger


class TurnstileCaptchaService(ICaptchaService):
    """
    implementation of ICaptchaService for Cloudflare Turnstile.
    """

    def __init__(self):
        self._secret_key = config.TURNSTILE_SECRET_KEY
        self._verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        self._logger = logger

    async def verify(self, token: str, ip: str | None = None) -> bool:
        """
        verifies the captcha token by sending a POST request to Cloudflare's Turnstile API.
        """
        data = {
            "secret": self._secret_key,
            "response": token,
        }
        if ip:
            data["remoteip"] = ip

        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(self._verify_url, data=data, timeout=10)
                result = r.json()
                success = result.get("success", False)
                if success:
                    self._logger.info("[Turnstile] Captcha verified")
                else:
                    self._logger.warning(
                        "[Turnstile] Captcha verification failed: %s",
                        result.get("error-codes"),
                    )
                return success
            except httpx.RequestError as exc:
                self._logger.error("[Turnstile] Request failed: %s", exc)
                return False
