from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


@dataclass(kw_only=True)
class UserMFARecoveryCodeEntity(BaseEntity, AuditMixin):
    """
    Entity representing a user MFA recovery code in the system.
    """

    mfa_id: int = field(
        metadata={
            "description": "The ID of the MFA associated with this recovery code",
            "index": True,
            "on_delete": "cascade",
        },
    )

    hashed_recovery_code: str = field(
        metadata={
            "description": "The hashed recovery code for MFA",
            "index": True,
        },
    )

    is_revoked: bool = field(
        default=False,
        metadata={
            "description": "Whether the recovery code has been revoked",
        },
    )

    def revoke(self) -> None:
        """
        Revoke the recovery code.
        """
        self.is_revoked = True
        self.mark_updated()
