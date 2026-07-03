from abc import abstractmethod
from typing import TypeVar

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.repository.organization_repository_interface import (
    IOrganizationRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    ServerError,
)
from src.shared.infrastructure.audit.audit_writer import write_audit_event

TEntity = TypeVar("TEntity", bound=BaseEntity)


def _build_conditions(criteria: dict):
    """
    Build SQL conditions dynamically supporting operators:
    gt, gte, lt, lte, ne, in, ilike, and NULL handling.
    """
    conditions = []
    params = {}

    for key, value in criteria.items():
        if value is None:
            conditions.append(f"{key} IS NULL")
            continue

        if "__" in key:
            column, op = key.split("__", 1)
            param_key = f"{column}_{op}"

            if op == "gt":
                conditions.append(f"{column} > :{param_key}")
            elif op == "gte":
                conditions.append(f"{column} >= :{param_key}")
            elif op == "lt":
                conditions.append(f"{column} < :{param_key}")
            elif op == "lte":
                conditions.append(f"{column} <= :{param_key}")
            elif op == "ne":
                conditions.append(f"{column} != :{param_key}")
            elif op == "in":
                conditions.append(f"{column} = ANY(:{param_key})")
            elif op == "ilike":
                conditions.append(f"{column} ILIKE :{param_key}")
            else:
                raise ValueError(f"Unsupported operator: {op}")

            params[param_key] = value

        else:
            conditions.append(f"{key} = :{key}")
            params[key] = value

    return " AND ".join(conditions), params


class OrganizationRepository[TEntity](IOrganizationRepository[TEntity]):
    """
    Generic repository enforcing strict organization-level isolation.

    All queries and mutations are automatically scoped to a single organization
    to guarantee multi-tenant safety at the persistence layer.
    """

    def __init__(self, session, table_name: str, organization_id: int):
        self.session = session
        self.table_name = table_name
        self.organization_id = organization_id

    def _org_filter_sql(self) -> str:
        """Returns SQL condition for organization scoping."""
        return "organization_id = :org_id"

    def _org_params(self, params: dict | None = None) -> dict:
        """Injects organization_id into query parameters."""
        params = params or {}
        params["org_id"] = self.organization_id
        return params

    def _enforce_org_write(self, row: dict) -> dict:
        """
        Ensures write operations cannot cross tenant boundaries.
        """
        if "organization_id" in row and row["organization_id"] != self.organization_id:
            raise ServerError("Cross-tenant write detected")

        row.pop("organization_id", None)
        row["organization_id"] = self.organization_id
        return row

    def _is_audit_table(self) -> bool:
        """Checks if current table is the audit log table."""
        return self.table_name == "sys_audit_logs"

    async def _emit_audit_event(
        self,
        *,
        action: str,
        entity_id: int | None,
        before_data: dict | None,
        after_data: dict | None,
    ) -> None:
        """Writes audit logs for entity changes."""
        await write_audit_event(
            session=self.session,
            action=action,
            entity_table=self.table_name,
            entity_id=entity_id,
            before_data=before_data,
            after_data=after_data,
        )

    @abstractmethod
    def to_row(self, entity: TEntity) -> dict:
        """Maps domain entity to database row format."""

    @abstractmethod
    def to_entity(self, row: dict) -> TEntity:
        """Maps database row to domain entity."""

    async def add(self, entity: TEntity, *, audit: bool = True) -> TEntity:
        """
        Creates a new entity within the organization scope.
        """
        row = self._enforce_org_write(self.to_row(entity))

        if row.get("id") is None:
            row.pop("id")

        columns = ", ".join(row.keys())
        placeholders = ", ".join(f":{k}" for k in row.keys())

        sql = text(
            f"INSERT INTO {self.table_name} ({columns}) "
            f"VALUES ({placeholders}) RETURNING *"
        )

        try:
            result = await self.session.execute(sql, row)
            inserted = dict(result.mappings().one())

            if audit and not self._is_audit_table():
                await self._emit_audit_event(
                    action="create",
                    entity_id=inserted.get("id"),
                    before_data={},
                    after_data=inserted,
                )

            return self.to_entity(inserted)

        except IntegrityError as e:
            raise ConflictError("Record already exists", str(e)) from e
        except SQLAlchemyError as e:
            raise CreateError("Failed to create record", str(e)) from e

    async def get_by_id(self, entity_id: int) -> TEntity | None:
        """Fetches an entity by ID within the organization scope."""
        sql = text(f"""
            SELECT * FROM {self.table_name}
            WHERE id = :id AND {self._org_filter_sql()}
            """)

        result = await self.session.execute(
            sql,
            {"id": entity_id, **self._org_params()},
        )

        row = result.mappings().one_or_none()
        return self.to_entity(dict(row)) if row else None

    async def get_by_uuid(self, entity_uuid: str) -> TEntity | None:
        """Fetches an entity by UUID within the organization scope."""
        sql = text(f"""
            SELECT * FROM {self.table_name}
            WHERE uuid = :uuid AND {self._org_filter_sql()}
            """)

        result = await self.session.execute(
            sql,
            {"uuid": entity_uuid, **self._org_params()},
        )

        row = result.mappings().one_or_none()
        return self.to_entity(dict(row)) if row else None

    async def get_by(self, **criteria) -> TEntity | None:
        """Fetches a single entity using dynamic filters within organization scope."""
        base = f"SELECT * FROM {self.table_name} WHERE {self._org_filter_sql()}"
        params = self._org_params()

        if criteria:
            conditions, extra = _build_conditions(criteria)
            base += f" AND {conditions}"
            params.update(extra)

        sql = text(base + " LIMIT 1")

        result = await self.session.execute(sql, params)
        row = result.mappings().one_or_none()

        return self.to_entity(dict(row)) if row else None

    async def update(self, entity: TEntity, *, audit: bool = True) -> TEntity:
        """Updates an entity within the organization scope."""
        entity_id = getattr(entity, "id", None)
        if not isinstance(entity_id, int):
            raise ValueError("Entity must have id")

        row = self._enforce_org_write(self.to_row(entity))
        updates = {k: v for k, v in row.items() if k != "id"}

        # Capture the pre-update state (org-scoped) for the audit trail.
        before: dict | None = None
        if audit and not self._is_audit_table():
            before_result = await self.session.execute(
                text(
                    f"SELECT * FROM {self.table_name} "
                    f"WHERE id = :id AND {self._org_filter_sql()}"
                ),
                {"id": entity_id, **self._org_params()},
            )
            before_row = before_result.mappings().one_or_none()
            before = dict(before_row) if before_row else None

        set_clause = ", ".join(f"{k} = :{k}" for k in updates)

        sql = text(f"""
            UPDATE {self.table_name}
            SET {set_clause}
            WHERE id = :id AND {self._org_filter_sql()}
            RETURNING *
            """)

        result = await self.session.execute(
            sql,
            {
                **updates,
                "id": entity_id,
                **self._org_params(),
            },
        )

        updated = dict(result.mappings().one())

        if audit and not self._is_audit_table():
            await self._emit_audit_event(
                action="update",
                entity_id=entity_id,
                before_data=before,
                after_data=updated,
            )

        return self.to_entity(updated)

    async def delete(self, entity_id: int, audit: bool = True) -> None:
        """Deletes an entity within the organization scope."""
        sql = text(f"""
            DELETE FROM {self.table_name}
            WHERE id = :id AND {self._org_filter_sql()}
            """)

        await self.session.execute(
            sql,
            {"id": entity_id, **self._org_params()},
        )

        await self.session.flush()

    async def filter(self, **criteria) -> list[TEntity]:
        """Retrieves multiple entities using dynamic filters within organization scope."""
        base = f"SELECT * FROM {self.table_name} WHERE {self._org_filter_sql()}"
        params = self._org_params()

        if criteria:
            conditions, extra = _build_conditions(criteria)
            base += f" AND {conditions}"
            params.update(extra)

        sql = text(base)

        result = await self.session.execute(sql, params)
        rows = result.mappings().all()

        return [self.to_entity(dict(r)) for r in rows]
