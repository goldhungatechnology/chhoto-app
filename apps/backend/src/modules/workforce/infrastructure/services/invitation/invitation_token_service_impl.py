import hmac
import secrets

from src.modules.workforce.domain.services.invitation.invitation_token_service import (
    InvitationTokenService,
)
from src.shared.infrastructure.hasher.hasher import HasherService, hasher

RAW_TOKEN_BYTES = 32  # 256 bits → ~43 url-safe chars


class InvitationTokenServiceImpl(InvitationTokenService):
    """
    Concrete invitation-token service.

    - `generate_raw` uses `secrets.token_urlsafe` (CSPRNG, url-safe, no padding)
    - `hash` and `verify` delegate to the shared HasherService's deterministic
      (unsalted) SHA-256, which is required because we need to look rows up by
      hash — salted hashes would never match on lookup.
    - `verify` uses `hmac.compare_digest` for constant-time comparison.
    """

    def __init__(self, hasher_service: HasherService):
        self._hasher = hasher_service

    def generate_raw(self) -> str:
        """
        Generate a fresh, random token string.
        """
        return secrets.token_urlsafe(RAW_TOKEN_BYTES)

    def hash(self, raw_token: str) -> str:
        """
        Deterministically hash the raw token using the shared hasher's
        """
        return self._hasher.deterministic_hash(raw_token)

    def verify(self, raw_token: str, hashed_token: str) -> bool:
        """
        Verify a raw token against a stored hash using constant-time comparison.
        """
        return hmac.compare_digest(self.hash(raw_token), hashed_token)


def get_invitation_token_service() -> InvitationTokenServiceImpl:
    """
    Factory function. The shared `hasher` singleton has no per-request state,
    so this is safe to call from anywhere.
    """
    return InvitationTokenServiceImpl(hasher_service=hasher)
