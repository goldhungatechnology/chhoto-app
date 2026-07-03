from datetime import UTC, datetime, timedelta

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from src.core.config.settings import config
from src.shared.exceptions.base_exceptions import InvalidError, UnAuthorizedError


class TokenService:
    """
    A service for generating and validating tokens.
    """

    def __init__(self, algorithm: str = "HS256", expiration_minutes: int = 60):
        self.secret_key = config.SECRET_KEY  # pyright: ignore[reportAttributeAccessIssue]
        self.algorithm = algorithm
        self.expiration_minutes = expiration_minutes

    def generate_token(
        self, data: dict, expiration_minutes: int | None = None
    ) -> tuple[str, datetime]:
        """
        Generates a JWT token with the given data.
        """

        expire = datetime.now(UTC) + timedelta(
            minutes=(
                expiration_minutes if expiration_minutes else self.expiration_minutes
            )
        )
        token_payload = {**data, "exp": expire}
        encoded_jwt = jwt.encode(
            token_payload, self.secret_key, algorithm=self.algorithm
        )
        return encoded_jwt, expire

    def validate_token(self, token: str) -> dict:
        """
        Validates the given JWT token and returns the decoded data if valid.
        """

        try:
            decoded_token = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return decoded_token
        except ExpiredSignatureError as e:
            raise UnAuthorizedError(
                error="Token has expired", internal_details=str(e)
            ) from e
        except InvalidTokenError as e:
            raise InvalidError(error="Invalid token", internal_details=str(e)) from e

    def random_token(self, digit: int = 6) -> str:
        """
        Generates a cryptographically secure random numeric token with the
        specified number of digits (used for short, user-typed OTP codes such
        as email verification). Uses `secrets` rather than `random` so the
        value is not predictable.
        """
        import secrets

        range_start = 10 ** (digit - 1)
        range_end = (10**digit) - 1
        span = range_end - range_start + 1
        return str(range_start + secrets.randbelow(span))

    def secure_token(self, nbytes: int = 32) -> str:
        """
        Generates a high-entropy, URL-safe token suitable for security-critical
        flows embedded in links (e.g. password reset), where the token is the
        sole credential and must be infeasible to brute-force or match across
        users.
        """
        import secrets

        return secrets.token_urlsafe(nbytes)
