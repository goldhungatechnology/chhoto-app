"""User MFA model added

Revision ID: e90e1f82759a
Revises: f16c2c4a8598
Create Date: 2026-04-29 16:06:47.491256

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "e90e1f82759a"
down_revision: Union[str, Sequence[str], None] = "f16c2c4a8598"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class UserMFAMigration(BaseMigration):
    table_name = "sys_auth_user_mfas"

    def __init__(self):
        super().__init__(revision="e90e1f82759a", down_revision="f16c2c4a8598")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.audit_mixin_columns()

        self.foreign(
            "user_id", "sys_auth_users", ondelete="cascade", nullable=False, index=True
        )
        self.string("secret", nullable=False)
        self.string("method", nullable=False)

        ## Optional fields
        self.string("auth_url", nullable=True, default=None)
        self.date_time("verified_at", nullable=True, default=None)
        self.date_time("revoked_at", nullable=True, default=None)


def upgrade() -> None:
    """
    Function to create a table
    """
    UserMFAMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    UserMFAMigration().downgrade()
