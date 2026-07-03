from fastapi.requests import Request
from starlette.responses import RedirectResponse
from src.core.config.settings import config
from src.modules.auth.infrastructure.oauth.interface.oauth_provider_interface import (
    IOAuthProvider,
    OAuthUserInfo,
)
from authlib.integrations.starlette_client import OAuth


class GoogleOAuthProvider(IOAuthProvider):
    """
    Google OAuth Provider implementation.
    """

    def __init__(self):
        self.oauth = OAuth()

        self.oauth.register(
            name="google",
            client_id=config.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=config.GOOGLE_OAUTH_CLIENT_SECRET,
            server_metadata_url=(
                "https://accounts.google.com/.well-known/openid-configuration"
            ),
            client_kwargs={"scope": "openid email profile"},
        )

        self.client = self.oauth.create_client("google")

    async def authorize_redirect(self, request: Request) -> RedirectResponse:
        """
        Get the authorization URL for Google OAuth.
        """

        redirect_uri = f"{config.APP_URL}/api/v1/auth/oauth/callback/google"

        return await self.client.authorize_redirect(request, redirect_uri)

    async def get_user(self, request: Request) -> OAuthUserInfo:
        """
        Get the user information from Google OAuth.
         - Fetch the token using the authorization code.
         - Retrieve user information from Google using the token.
        """
        token = await self.client.authorize_access_token(request)
        user_info = token.get("userinfo")

        # Google may return email_verified as a bool or the string "true".
        email_verified = user_info.get("email_verified", False)
        if isinstance(email_verified, str):
            email_verified = email_verified.lower() == "true"

        return OAuthUserInfo(
            email=user_info["email"],
            provider_user_id=user_info["sub"],
            email_verified=bool(email_verified),
            name=user_info.get("name"),
            avatar_url=user_info.get("picture"),
        )
