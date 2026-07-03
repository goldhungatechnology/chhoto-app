# Skill: Database Guidelines

This document details database architecture and migration rules for AI coding agents.

## Repository Pattern and Transactions
- Define repository operations in interfaces inside `domain/repositories/`.
- Implement interfaces inside `infrastructure/repositories/` using SQLAlchemy's `AsyncSession`.
- Never run `.commit()` inside repositories. All transactions must be committed at the application layer using the Unit of Work pattern (`BaseUOW` or specific context UOWs).

## Migration Protocols
- Generate Alembic migrations using `make migration name=<migration_name> msg="<message>"`.
- Use the imperative table design pattern by subclassing `BaseMigration` from `migrations/base.py` for structured migrations:
  ```python
  from migrations.base import BaseMigration
  
  class CreateUsersTableMigration(BaseMigration):
      table_name = "sys_auth_users"
      def __init__(self):
          super().__init__(revision="xxx", down_revision="yyy")
          self.base_columns()
          self.string("email", nullable=False, unique=True)
          self.string("password_hash", nullable=False)
  ```
- Always implement both the `upgrade()` and `downgrade()` methods in your migrations.
