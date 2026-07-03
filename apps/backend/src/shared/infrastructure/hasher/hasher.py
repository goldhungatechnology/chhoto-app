import hmac

from argon2 import PasswordHasher


class HasherService:
    """
    Service for hashing and verifying passwords using Argon2.
    """

    def __init__(self):
        self.hasher = PasswordHasher()
        # A fixed dummy hash used to spend the same CPU time on login misses as
        # on a real verification, so response timing does not reveal whether an
        # account exists (user-enumeration timing oracle).
        self._dummy_hash = self.hasher.hash("dummy-password-for-constant-time")

    def hash(self, plain_password: str) -> str:
        """
        Hashes a plain text
        """
        return self.hasher.hash(plain_password)

    def verify(self, hashed_password: str, plain_password: str) -> bool:
        """
        Verifies a plain text against a hashed text.
        """
        try:
            return self.hasher.verify(hashed_password, plain_password)
        except Exception:
            return False

    def dummy_verify(self, plain_password: str) -> None:
        """
        Perform a throwaway verification against a fixed dummy hash to equalize
        timing on paths where no real account/hash is available.
        """
        self.verify(self._dummy_hash, plain_password)

    def deterministic_hash(self, value: str) -> str:
        """
        Hashes a value in a deterministic way, meaning the same input will always produce the same output.
         This is useful for hashing values that need to be compared later, such as tokens or identifiers.
         Note: This method is not suitable for hashing passwords, as it does not use a random salt.
         Use the `hash` method for password hashing instead.
        """
        import hashlib

        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def verify_deterministic_hash(self, value: str, hashed_value: str) -> bool:
        """
        Verifies a value against a deterministic hash using a constant-time
        comparison to avoid leaking information through timing.
        """
        return hmac.compare_digest(self.deterministic_hash(value), hashed_value)


hasher = HasherService()
