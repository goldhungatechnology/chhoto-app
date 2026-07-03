"""User Token model added

Revision ID: 031959c695dd
Revises: 65deda53b736
Create Date: 2026-04-29 16:29:33.761665

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "031959c695dd"
down_revision: Union[str, Sequence[str], None] = "65deda53b736"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class UserTokenMigration(BaseMigration):
    table_name = "sys_auth_user_tokens"

    def __init__(self):
        super().__init__(revision="031959c695dd", down_revision="65deda53b736")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.audit_mixin_columns()
        self.foreign(
            "user_id", "sys_auth_users", ondelete="cascade", nullable=False, index=True
        )
        self.string("type", nullable=False, index=True)
        self.string("token_hash", nullable=False, index=True)
        self.date_time("expires_at", nullable=False, index=True)

        ## Optional fields
        self.date_time("used_at", nullable=True, default=None)


def upgrade() -> None:
    """
    Function to create a table
    """
    UserTokenMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    UserTokenMigration().downgrade()
