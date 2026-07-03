"""User Session model added

Revision ID: bd023f4fd3a3
Revises: 544fc66a1363
Create Date: 2026-04-29 16:05:56.916291

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "bd023f4fd3a3"
down_revision: Union[str, Sequence[str], None] = "544fc66a1363"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class UserSessionMigration(BaseMigration):
    table_name = "sys_auth_user_sessions"

    def __init__(self):
        super().__init__(revision="bd023f4fd3a3", down_revision="544fc66a1363")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.audit_mixin_columns()

        self.foreign(
            "user_id", "sys_auth_users", ondelete="cascade", nullable=False, index=True
        )
        self.date_time("expires_at", nullable=False)

        ## Optional fields
        self.string("ip_address", nullable=True, default=None)
        self.string("device", nullable=True, default=None)
        self.string("browser", nullable=True, default=None)
        self.date_time("revoked_at", nullable=True, default=None)
        self.string("organization_uuid", nullable=True, default=None)


def upgrade() -> None:
    """
    Function to create a table
    """
    UserSessionMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    UserSessionMigration().downgrade()
