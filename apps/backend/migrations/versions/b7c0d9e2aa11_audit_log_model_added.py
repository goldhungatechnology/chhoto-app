"""Audit log model added

Revision ID: b7c0d9e2aa11
Revises: 031959c695dd
Create Date: 2026-07-03 16:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from migrations.base import BaseMigration

revision: str = "b7c0d9e2aa11"
down_revision: Union[str, Sequence[str], None] = "031959c695dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class AuditLogModelMigration(BaseMigration):
    table_name = "sys_audit_logs"

    def __init__(self):
        super().__init__(revision=revision, down_revision="031959c695dd")
        self.create_whole_table = True
        self.base_columns()

        self.string("action", length=64, nullable=False, index=True)
        self.string("entity_table", nullable=False, index=True)
        self.integer("entity_id", nullable=True, index=True)
        self.text("before_data", nullable=True, default=None)
        self.text("after_data", nullable=True, default=None)
        self.foreign(
            "actor_id",
            "sys_auth_users",
            ondelete="SET NULL",
            nullable=True,
            index=True,
        )
        self.string("request_id", nullable=True, default=None, index=True)
        self.string("client_ip", nullable=True, default=None)
        self.string("client_country", nullable=True, default=None)
        self.string("client_city", nullable=True, default=None)
        self.text("user_agent", nullable=True, default=None)

        self.fields.append(
            sa.Index(
                "ix_sys_audit_logs_entity_table_entity_id",
                "entity_table",
                "entity_id",
            )
        )


def upgrade() -> None:
    """
    Function to create table.
    """
    AuditLogModelMigration().upgrade()


def downgrade() -> None:
    """
    Function to drop table.
    """
    AuditLogModelMigration().downgrade()
