"""User model added

Revision ID: 47b8bde515a6
Revises: ab3035ecb04c
Create Date: 2026-04-29 16:00:32.847385

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "47b8bde515a6"
down_revision: Union[str, Sequence[str], None] = "ab3035ecb04c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class UserModelMigration(BaseMigration):
    table_name = "sys_auth_users"

    def __init__(self):
        super().__init__(revision="47b8bde515a6", down_revision="ab3035ecb04c")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.audit_mixin_columns()
        self.soft_delete_mixin_column()

        self.string("username", nullable=False, unique=True, index=True)
        self.string("email", nullable=False, unique=True, index=True)
        self.string("avatar_bg", nullable=False)
        self.boolean("is_onboarded", nullable=False)
        self.string("status", nullable=False, default="active")

        ## Optional fields
        self.string("full_name", nullable=True, default=None)
        self.string("avatar", nullable=True, default=None)
        self.string("phone_number", nullable=True, default=None)
        self.foreign(
            "country_id",
            "sys_countries",
            ondelete="SET NULL",
            nullable=True,
            index=True,
        )
        self.date_time("email_verified_at", nullable=True, default=None)


def upgrade() -> None:
    """
    Function to create a table
    """
    UserModelMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    UserModelMigration().downgrade()
