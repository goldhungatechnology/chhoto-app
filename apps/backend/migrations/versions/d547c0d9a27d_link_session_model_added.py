"""link session model added

Revision ID: d547c0d9a27d
Revises: e44e84a97c42
Create Date: 2026-07-18 09:01:09.695332

"""

from typing import Sequence, Union

from migrations.base import BaseMigration

revision: str = "d547c0d9a27d"
down_revision: Union[str, Sequence[str], None] = "e44e84a97c42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class LinkSessionTableMigration(BaseMigration):
    table_name = "sys_link_sessions"

    def __init__(self):
        super().__init__(revision="d547c0d9a27d", down_revision="e44e84a97c42")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.foreign(
            "link_id",
            "sys_links",
            ondelete="cascade",
            index=True,
        )
        self.string("ip_address", length=255, nullable=True, default=None)
        self.string("device", length=255, nullable=True, default=None)
        self.string("browser", length=255, nullable=True, default=None)
        self.string("referral_source", length=255, nullable=True, default=None)


def upgrade() -> None:
    """
    Function to create a table
    """
    LinkSessionTableMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    LinkSessionTableMigration().downgrade()
