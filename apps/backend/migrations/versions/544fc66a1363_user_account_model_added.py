"""User Account model added

Revision ID: 544fc66a1363
Revises: 47b8bde515a6
Create Date: 2026-04-29 16:05:38.940393

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "544fc66a1363"
down_revision: Union[str, Sequence[str], None] = "47b8bde515a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class UserAccountMigration(BaseMigration):
    table_name = "sys_auth_user_accounts"

    def __init__(self):
        super().__init__(revision="544fc66a1363", down_revision="47b8bde515a6")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.string("type", nullable=False)
        self.foreign(
            "user_id", "sys_auth_users", ondelete="cascade", nullable=False, index=True
        )

        ## Optional fields
        self.string("hashed_password", nullable=True, default=None)
        self.string("provider", nullable=True, default=None)
        self.date_time("last_password_updated_at", nullable=True, default=None)


def upgrade() -> None:
    """
    Function to create a table
    """
    UserAccountMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    UserAccountMigration().downgrade()
