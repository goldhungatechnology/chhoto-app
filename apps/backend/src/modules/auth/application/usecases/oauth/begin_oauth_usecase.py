from typing import Literal

from fastapi.requests import Request
from starlette.responses import RedirectResponse


class BeginOAuthUseCase:
    """
    Use case for beginning the OAuth flow by getting the authorization URL for a given provider.
    """

    async def execute(
        self, provider: Literal["google"], request: Request
    ) -> RedirectResponse:
        """
        Get the authorization URL for the specified OAuth provider.
        """
        from src.modules.auth.infrastructure.oauth.oauth_factory import OAuthFactory

        oauth_provider = OAuthFactory.get_provider(provider)

        return await oauth_provider.authorize_redirect(request)
