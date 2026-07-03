from abc import ABC, abstractmethod


class ICaptchaService(ABC):
    """
    Interface for captcha services.
    """

    @abstractmethod
    async def verify(self, token: str, ip: str | None = None) -> bool:
        """
        Verifies the captcha token.
        """
        raise NotImplementedError
