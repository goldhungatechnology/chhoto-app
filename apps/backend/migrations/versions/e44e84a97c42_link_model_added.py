"""link model added

Revision ID: e44e84a97c42
Revises: b7c0d9e2aa11
Create Date: 2026-07-18 09:00:57.670396

"""

from typing import Sequence, Union

from migrations.base import BaseMigration

revision: str = "e44e84a97c42"
down_revision: Union[str, Sequence[str], None] = "b7c0d9e2aa11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class LinkTableMigration(BaseMigration):
    table_name = "sys_links"

    def __init__(self):
        super().__init__(revision="e44e84a97c42", down_revision="b7c0d9e2aa11")
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.foreign(
            "user_id", "sys_auth_users", ondelete="cascade", index=True, nullable=False
        )
        self.text("destination_url", nullable=False)
        self.string("short_url", length=255, unique=True, index=True, nullable=False)
        self.array("tags", item_type="String", nullable=True)
        self.date_time("auto_expire", nullable=True)
        self.biginteger("total_clicks", nullable=False, default=0)
        self.string("title", length=255, nullable=True, default=None)


def upgrade() -> None:
    """
    Function to create a table
    """
    LinkTableMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop a table
    """
    LinkTableMigration().downgrade()
