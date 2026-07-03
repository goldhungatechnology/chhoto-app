from abc import ABC, abstractmethod
from dataclasses import dataclass
from fastapi.requests import Request
from starlette.responses import RedirectResponse


@dataclass
class OAuthUserInfo:
    """
    user info from oauth provider
    """

    email: str
    provider_user_id: str
    email_verified: bool = False
    name: str | None = None
    avatar_url: str | None = None
    ip_address: str | None = None
    device: str | None = None
    browser: str | None = None


class IOAuthProvider(ABC):
    """
    interfaces for oauth provider
    """

    @abstractmethod
    async def authorize_redirect(self, request: Request) -> RedirectResponse:
        """
        get redirect url for oauth provider authorization
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, request: Request) -> OAuthUserInfo:
        """
        get user info from oauth provider by access token in request
        """
        raise NotImplementedError
