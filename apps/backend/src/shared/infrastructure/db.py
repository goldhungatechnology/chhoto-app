from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.core.config.settings import config

DATABASE_URL: str = config.DATABASE_URL

# Create async engine and sessionmaker
async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Create sync engine for migrations if needed (replacing driver with psycopg2)
sync_engine = create_engine(
    DATABASE_URL.replace("asyncpg", "psycopg2"), echo=False, future=True
)

Base = declarative_base()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an asynchronous database session.
    """
    async with async_session() as session:
        yield session


def create_worker_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Create a new async engine + session factory bound to the current event loop.
    Useful for background workers running on separate event loops.
    """
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
