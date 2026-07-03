from typing import Literal

from src.modules.auth.infrastructure.oauth.interface.oauth_provider_interface import (
    IOAuthProvider,
)


class OAuthFactory:
    """
    Factory class for creating OAuth instances.
    """

    @staticmethod
    def get_provider(provider_name: Literal["google"]) -> IOAuthProvider:
        """
        Get the OAuth provider instance based on the provider name.
        """

        match provider_name:
            case "google":
                from src.modules.auth.infrastructure.oauth.providers.google_oauth_provider import (
                    GoogleOAuthProvider,
                )

                return GoogleOAuthProvider()

            case _:
                raise ValueError(f"Unsupported OAuth provider: {provider_name}")
