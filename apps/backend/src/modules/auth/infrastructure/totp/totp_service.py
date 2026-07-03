import base64
import hashlib
import hmac
import struct
import time

from src.core.config.settings import config


class TOTPService:
    """
    Service for TOTP generation and verification (RFC 6238).
    """

    def __init__(self, issuer: str | None = None):
        self.issuer = issuer or config.PROJECT_NAME or "Chatboq"

    def generate_secret(self) -> str:
        """
        Generate a random base32-encoded secret key for TOTP.
        """
        import secrets

        random_bytes = secrets.token_bytes(20)
        return base64.b32encode(random_bytes).decode("utf-8")

    def generate_auth_url(self, secret: str, email: str) -> str:
        """
        Generate an otpauth:// URL for provisioning a TOTP authenticator app.
        """
        import urllib.parse

        params = urllib.parse.urlencode(
            {
                "secret": secret,
                "issuer": self.issuer,
                "algorithm": "SHA1",
                "digits": 6,
                "period": 30,
            }
        )
        encoded_issuer = urllib.parse.quote(self.issuer)
        encoded_email = urllib.parse.quote(email)
        return f"otpauth://totp/{encoded_issuer}:{encoded_email}?{params}"

    def verify_totp(self, secret: str, otp: str, drift_steps: int = 1) -> bool:
        """
        Verify a TOTP code against the given secret.

        Allows a time drift of ±drift_steps intervals (default 1 step = 30s)
        to account for clock skew.
        """
        try:
            secret_bytes = base64.b32decode(secret, casefold=True)
        except Exception:
            return False

        if not otp.isdigit() or len(otp) != 6:
            return False

        current_time = int(time.time())
        time_step = 30

        for offset in range(-drift_steps, drift_steps + 1):
            counter = (current_time // time_step) + offset
            expected = self._generate_otp(secret_bytes, counter)
            if hmac.compare_digest(expected, otp):
                return True

        return False

    def _generate_otp(self, secret_bytes: bytes, counter: int) -> str:
        """
        Generate a 6-digit OTP for the given counter using HMAC-SHA1.
        """
        counter_bytes = struct.pack(">Q", counter)
        hmac_hash = hmac.new(secret_bytes, counter_bytes, hashlib.sha1).digest()

        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack(">I", hmac_hash[offset : offset + 4])[0] & 0x7FFFFFFF
        return str(truncated % 1_000_000).zfill(6)
