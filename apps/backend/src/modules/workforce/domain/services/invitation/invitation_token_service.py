from abc import ABC, abstractmethod


class InvitationTokenService(ABC):
    """
    Domain-side abstraction for invitation token operations.

    Splits the "what" (a random secret token, a deterministic hash for
    lookup) from the "how" (specific RNG, specific hash algorithm). The
    InvitationDomainService depends only on this interface, keeping the
    domain free of `secrets`, `hashlib`, and any specific hasher instance.
    """

    @abstractmethod
    def generate_raw(self) -> str:
        """
        Produce a fresh, cryptographically-strong, URL-safe token. Each call
        MUST return a unique value; collisions are the caller's responsibility
        to detect via the uniqueness constraint on `hashed_token`.
        """

    @abstractmethod
    def hash(self, raw_token: str) -> str:
        """
        Deterministically hash a raw token. The same input MUST always yield
        the same output (so we can look up rows by hashing the user-supplied
        token at request time). Non-reversible — raw tokens must never be
        recovered from the hash.
        """

    @abstractmethod
    def verify(self, raw_token: str, hashed_token: str) -> bool:
        """
        Constant-time compare a raw token against a previously-stored hash.
        """
