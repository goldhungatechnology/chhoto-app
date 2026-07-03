from abc import abstractmethod
from typing import TypeVar

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    CreateError,
    DeleteError,
    ServerError,
)
from src.shared.infrastructure.audit.audit_writer import write_audit_event

TEntity = TypeVar("TEntity", bound=BaseEntity)


def _build_conditions(criteria: dict):
    """
    build conditions to make the filter method more powerful, it supports operators like gt, gte, lt, lte, ne, in and also handles null values properly.
    """
    conditions = []
    params = {}

    for key, value in criteria.items():
        # -------------------------
        # NULL handling (IMPORTANT)
        # -------------------------
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


class BaseRepository[TEntity](IBaseRepository[TEntity]):
    """
    implementation of the base repository with explicit mapping between domain entity and database row, it also includes audit event emission for create, update and delete operations.
    """

    def __init__(self, session, table_name: str):
        self.session = session
        self.table_name = table_name

    def _is_audit_table(self) -> bool:
        return self.table_name == "sys_audit_logs"

    async def _get_row_map_by_id(self, entity_id: int) -> dict | None:
        sql = text(f"SELECT * FROM {self.table_name} WHERE id = :id LIMIT 1")
        result = await self.session.execute(sql, {"id": entity_id})
        row = result.mappings().one_or_none()
        return dict(row) if row else None

    # -----------------------------
    # AUDIT HELPERS
    # -----------------------------
    async def _emit_audit_event(
        self,
        *,
        action: str,
        entity_id: int | None,
        before_data: dict | None,
        after_data: dict | None,
    ) -> None:
        await write_audit_event(
            session=self.session,
            action=action,
            entity_table=self.table_name,
            entity_id=entity_id,
            before_data=before_data,
            after_data=after_data,
        )

    @staticmethod
    def _select_audit_fields(data: dict | None, fields: set[str] | None) -> dict:
        if fields is None or data is None:
            return {}
        return {k: v for k, v in data.items() if k in fields}

    # -----------------------------
    # ABSTRACT MAPPERS
    # -----------------------------
    @abstractmethod
    def to_row(self, entity: TEntity) -> dict:
        """
        Convert a domain entity to a dictionary representing a database row.
        """

    @abstractmethod
    def to_entity(self, row: dict) -> TEntity:
        """
        Convert a database row (as a dictionary) back to a domain entity.
        """

    # -----------------------------
    # CREATE
    # -----------------------------
    async def add(self, entity: TEntity, *, audit: bool = True) -> TEntity:
        """
        implementation of the add method that converts the entity to a row, constructs an insert statement, executes it and then converts the inserted row back to an entity. It also emits an audit event if auditing is enabled and the table is not an audit table itself.
        """
        row = {k: v for k, v in self.to_row(entity).items() if k != "id"}
        columns = ", ".join(row.keys())
        placeholders = ", ".join(f":{k}" for k in row.keys())

        sql = text(
            f"INSERT INTO {self.table_name} ({columns}) "
            f"VALUES ({placeholders}) RETURNING *"
        )

        try:
            result = await self.session.execute(sql, row)
            inserted = result.mappings().one()
            inserted_row = dict(inserted)

            if audit and not self._is_audit_table():
                await self._emit_audit_event(
                    action="create",
                    entity_id=inserted_row.get("id"),
                    before_data={},
                    after_data=inserted_row,
                )

            return self.to_entity(inserted_row)

        except IntegrityError as e:
            raise ConflictError("Record already exists", str(e)) from e
        except SQLAlchemyError as e:
            raise CreateError("Failed to create record", str(e)) from e

    # -----------------------------
    # READ
    # -----------------------------
    async def get_by_id(self, entity_id: int) -> TEntity | None:
        """
        implementation of the get_by_id method that constructs a select statement to fetch a record by its id, executes it and converts the result to an entity. It returns None if no record is found.
        """
        sql = text(f"SELECT * FROM {self.table_name} WHERE id = :id LIMIT 1")
        try:
            result = await self.session.execute(sql, {"id": entity_id})
            row = result.mappings().one_or_none()
            return self.to_entity(dict(row)) if row else None
        except SQLAlchemyError as e:
            raise ServerError("Failed to fetch record by id", str(e)) from e

    async def get_by_uuid(self, entity_uuid: str) -> TEntity | None:
        """
        implementation of the get_by_uuid method that constructs a select statement to fetch a record by its uuid, executes it and converts the result to an entity. It returns None if no record is found.
        """
        sql = text(f"SELECT * FROM {self.table_name} WHERE uuid = :uuid LIMIT 1")
        try:
            result = await self.session.execute(sql, {"uuid": entity_uuid})
            row = result.mappings().one_or_none()
            return self.to_entity(dict(row)) if row else None
        except SQLAlchemyError as e:
            raise ServerError("Failed to fetch record by uuid", str(e)) from e

    async def get_by(self, **criteria) -> TEntity | None:
        """
        implementation of the get_by method that builds dynamic conditions based on the provided criteria, constructs a select statement, executes it and converts the result to an entity. It returns None if no record is found.
        """
        conditions, params = _build_conditions(criteria)
        sql = text(f"SELECT * FROM {self.table_name} WHERE {conditions} LIMIT 1")

        try:
            result = await self.session.execute(sql, params)
            row = result.mappings().one_or_none()
            return self.to_entity(dict(row)) if row else None
        except SQLAlchemyError as e:
            raise ServerError("Failed to fetch record", str(e)) from e

    # -----------------------------
    # UPDATE
    # -----------------------------
    async def update(self, entity: TEntity, *, audit: bool = True) -> TEntity:
        """
        update implementation that converts the entity to a row, constructs an update statement with dynamic set clauses based on the row data, executes it and then converts the updated row back to an entity. It also emits an audit event if auditing is enabled and the table is not an audit table itself. The method expects the entity to have a valid id for the update operation.
        """
        entity_id = getattr(entity, "id", None)
        if not isinstance(entity_id, int):
            raise ValueError("Entity must have id")

        row = self.to_row(entity)
        updates = {k: v for k, v in row.items() if k != "id"}

        set_clause = ", ".join(f"{k} = :{k}" for k in updates)

        sql = text(
            f"UPDATE {self.table_name} SET {set_clause} WHERE id = :id RETURNING *"
        )

        try:
            before = await self._get_row_map_by_id(entity_id)

            result = await self.session.execute(sql, {**updates, "id": entity_id})
            updated = result.mappings().one()
            updated_row = dict(updated)

            if audit and not self._is_audit_table():
                await self._emit_audit_event(
                    action="update",
                    entity_id=entity_id,
                    before_data=before,
                    after_data=updated_row,
                )

            return self.to_entity(updated_row)

        except SQLAlchemyError as e:
            raise ServerError("Failed to update record", str(e)) from e

    # -----------------------------
    # DELETE
    # -----------------------------
    async def delete(self, entity_id: int, audit: bool = True) -> None:
        """
        delete implementation that constructs a delete statement to remove a record by its id, executes it and emits an audit event if the table is not an audit table itself. The method expects a valid entity_id for the delete operation.
        """
        sql = text(f"DELETE FROM {self.table_name} WHERE id = :id")

        try:
            before = await self._get_row_map_by_id(entity_id)

            await self.session.execute(sql, {"id": entity_id})

            if before and audit and not self._is_audit_table():
                await self._emit_audit_event(
                    action="delete",
                    entity_id=entity_id,
                    before_data=before,
                    after_data=None,
                )

            await self.session.flush()

        except SQLAlchemyError as e:
            raise DeleteError("Failed to delete record", str(e)) from e

    # -----------------------------
    # FILTER (NOW POWERED BY OPERATORS)
    # -----------------------------
    async def filter(self, **criteria) -> list[TEntity]:
        """
        filter implementation that builds dynamic conditions based on the provided criteria, constructs a select statement, executes it and converts the results to a list of entities. It supports operators like gt, gte, lt, lte, ne, in and also handles null values properly.
        """
        try:
            if criteria:
                conditions, params = _build_conditions(criteria)
                sql = text(f"SELECT * FROM {self.table_name} WHERE {conditions}")
                result = await self.session.execute(sql, params)
            else:
                sql = text(f"SELECT * FROM {self.table_name}")
                result = await self.session.execute(sql)

            rows = result.mappings().all()
            return [self.to_entity(dict(r)) for r in rows]

        except SQLAlchemyError as e:
            raise ServerError("Failed to filter records", str(e)) from e
