import os

import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.core.config.settings import config

if not config.is_testing:
    raise RuntimeError(
        "Tests must be run with the TESTING environment variable set to true"
    )


@pytest_asyncio.fixture(scope="session")
async def setup_test_environment():
    """
    Fixture to set up the test environment before any tests run.
    """
    print("\nTest environment setup complete.\n")
    # Point to the root alembic.ini
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "../alembic.ini"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url", str(config.DATABASE_URL.replace("asyncpg", "psycopg2"))
    )
    # Automatically apply all migrations to the test database
    command.upgrade(alembic_cfg, "head")

    yield

    # Clean up test database
    engine = create_async_engine(config.DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: sync_conn.execute(text("DROP SCHEMA public CASCADE"))
        )
        await conn.run_sync(
            lambda sync_conn: sync_conn.execute(text("CREATE SCHEMA public"))
        )

    from src.shared.infrastructure.db import async_engine as module_async_engine

    await module_async_engine.dispose()
    print("\nTest environment destroy complete.\n")
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_engine(setup_test_environment):
    """
    Function-scoped test engine setup.
    """
    engine = create_async_engine(config.DATABASE_URL, future=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    """
    Yields an AsyncSession wrapper over a transaction rollback.
    """
    conn = await test_engine.connect()
    await conn.begin()

    session = AsyncSession(
        bind=conn,
        expire_on_commit=False,
    )

    session.commit = session.flush

    yield session

    await session.close()
    await conn.rollback()
    await conn.close()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session):
    """
    Yields an AsyncClient bound to the FastAPI instance with database override.
    """
    from src.main import create_app
    from src.shared.infrastructure.db import get_async_session

    app = create_app()

    async def override_get_async_session():
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.clear()
