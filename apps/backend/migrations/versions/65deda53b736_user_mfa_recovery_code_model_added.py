"""User MFA recovery code model added

Revision ID: 65deda53b736
Revises: e90e1f82759a
Create Date: 2026-04-29 16:07:00.446038

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "65deda53b736"
down_revision: Union[str, Sequence[str], None] = "e90e1f82759a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class UserMFARecoveryCodeMigration(BaseMigration):
    table_name = "sys_auth_user_mfa_recovery_codes"

    def __init__(self):
        super().__init__(revision="65deda53b736", down_revision="e90e1f82759a")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.audit_mixin_columns()

        self.foreign(
            "mfa_id",
            "sys_auth_user_mfas",
            ondelete="cascade",
            nullable=False,
            index=True,
        )
        self.string("hashed_recovery_code", nullable=False, index=True)
        self.boolean("is_revoked", default=False, nullable=False)


def upgrade() -> None:
    """
    Function to create a table
    """
    UserMFARecoveryCodeMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    UserMFARecoveryCodeMigration().downgrade()
