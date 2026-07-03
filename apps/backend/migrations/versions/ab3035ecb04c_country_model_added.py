"""Country model added

Revision ID: ab3035ecb04c
Revises:
Create Date: 2026-06-10 11:45:47.584723

"""

import sqlalchemy as sa
from alembic import op
import uuid
from migrations.base import BaseMigration
from typing import Sequence, Union
from src.data.countries.default_countries import COUNTRIES

revision: str = "ab3035ecb04c"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class CountryModelMigration(BaseMigration):
    table_name = "sys_countries"

    def __init__(self):
        super().__init__(revision="ab3035ecb04c", down_revision=None)
        self.create_whole_table = True
        # describe your schemas here
        self.base_columns()
        self.soft_delete_mixin_column()
        self.string("name", length=255, nullable=False, index=True)
        self.string("iso_code_2", length=2, nullable=False)
        self.string("iso_code_3", length=3, nullable=False)
        self.string("phone_code", length=20, nullable=True)


def upgrade() -> None:
    """
    Function to create a table
    """
    migration = CountryModelMigration()
    migration.upgrade()
    country_table = sa.table(
        "sys_countries",
        sa.column("uuid", sa.String),
        sa.column("name", sa.String),
        sa.column("iso_code_2", sa.String),
        sa.column("iso_code_3", sa.String),
        sa.column("phone_code", sa.String),
    )

    seeded_countries = [
        {
            "uuid": str(uuid.uuid4()),
            "name": country["name"],
            "iso_code_2": country["iso2"],
            "iso_code_3": country["iso3"],
            "phone_code": country["phone_code"],
        }
        for country in COUNTRIES
    ]

    op.bulk_insert(country_table, seeded_countries)


def downgrade() -> None:
    """
    Function to drop a table
    """
    CountryModelMigration().downgrade()
