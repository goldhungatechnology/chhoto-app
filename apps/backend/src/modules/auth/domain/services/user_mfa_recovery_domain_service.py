import secrets
import string

from src.modules.auth.domain.entities.user_mfa_recovery_entity import (
    UserMFARecoveryCodeEntity,
)
from src.modules.auth.domain.repositories.user_mfa_recovery_repository import (
    IUserMFARecoveryRepository,
)
from src.shared.exceptions.base_exceptions import CreateError
from src.shared.infrastructure.hasher.hasher import HasherService


class UserMFARecoveryDomainService:
    """
    Service class for user MFA recovery code domain logic.
    """

    def __init__(
        self,
        repository: IUserMFARecoveryRepository,
        hasher_service: HasherService,
    ):
        self.repository = repository
        self.hasher_service = hasher_service

    def generate_recovery_codes(self, count: int = 8) -> list[str]:
        """
        Generates `count` random recovery codes in format XXXX-XXXX (e.g. 9B2A-7K4M).
        """
        alphabet = string.ascii_uppercase + string.digits
        codes = []
        for _ in range(count):
            part1 = "".join(secrets.choice(alphabet) for _ in range(4))
            part2 = "".join(secrets.choice(alphabet) for _ in range(4))
            codes.append(f"{part1}-{part2}")
        return codes

    async def create_recovery_codes_for_mfa(
        self, mfa_id: int, count: int = 8
    ) -> list[str]:
        """
        Generates recovery codes, hashes them, persists them for mfa_id,
        and returns the unhashed recovery codes.
        """
        try:
            plain_codes = self.generate_recovery_codes(count=count)
            entities = [
                UserMFARecoveryCodeEntity(
                    mfa_id=mfa_id,
                    hashed_recovery_code=self.hasher_service.hash(code),
                )
                for code in plain_codes
            ]
            await self.repository.add_many(entities)
            return plain_codes
        except Exception as e:
            raise CreateError(
                "Failed to generate recovery codes", internal_details=str(e)
            ) from e

    async def verify_recovery_code(self, mfa_id: int, plain_code: str) -> bool:
        """
        Verifies a plaintext recovery code against the active (non-revoked)
        recovery codes for the given MFA. If a match is found, the code is
        revoked (single-use) and True is returned.

        All active codes are checked even after a match is found to keep the
        verification time roughly constant, avoiding timing side-channels.
        """
        try:
            normalized = plain_code.strip().upper()
            active_codes = await self.repository.get_by_mfa_id(mfa_id)

            matched_code = None
            for code in active_codes:
                if self.hasher_service.verify(code.hashed_recovery_code, normalized):
                    matched_code = code

            if matched_code is None:
                return False

            matched_code.revoke()
            await self.repository.update(matched_code)
            return True
        except Exception as e:
            raise CreateError(
                "Failed to verify recovery code", internal_details=str(e)
            ) from e
