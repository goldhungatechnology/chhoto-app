from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ProvisionedUser:
    """
    Lightweight result type for a successful provisioning. Mirrors the shape
    returned by the regular signup use case so the same cookie/session
    handling can be reused at the API layer.
    """

    user_id: int
    user_uuid: str
    email: str
    username: str
    session_uuid: str
    session_expires_at: datetime


class UserProvisioner(ABC):
    """
    Cross-context write port for creating a fresh user account in a single
    atomic step. Used by flows that arrive with externally-verified email
    ownership (e.g. invitation acceptance, OAuth-bootstrapped signups) so
    that the user lands as ready-to-use without a separate verification
    round-trip.

    Standard `CreateUserUseCase` is the right path for self-service signups
    that still need to verify the email. Use this port ONLY when the email
    has already been proven (clicking an invitation link sent to that
    address counts).
    """

    @abstractmethod
    async def provision_invited_user(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> ProvisionedUser:
        """
        Create a verified, onboarded user with a fresh session. Raises
        ConflictError if an account already exists for the given email.
        """
