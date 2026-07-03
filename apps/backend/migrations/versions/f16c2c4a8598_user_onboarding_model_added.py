"""User Onboarding model added

Revision ID: f16c2c4a8598
Revises: bd023f4fd3a3
Create Date: 2026-04-29 16:06:23.784405

"""

from migrations.base import BaseMigration
from typing import Sequence, Union

revision: str = "f16c2c4a8598"
down_revision: Union[str, Sequence[str], None] = "bd023f4fd3a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class UserOnboardingMigration(BaseMigration):
    table_name = "sys_auth_user_onboardings"

    def __init__(self):
        super().__init__(revision="f16c2c4a8598", down_revision="bd023f4fd3a3")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.audit_mixin_columns()

        self.foreign(
            "user_id", "sys_auth_users", ondelete="cascade", nullable=False, index=True
        )
        self.string("theme", nullable=False, default="light")
        self.string("referral_source", nullable=True, default=None)


def upgrade() -> None:
    """
    Function to create a table
    """
    UserOnboardingMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    UserOnboardingMigration().downgrade()
