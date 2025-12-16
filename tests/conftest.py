"""Pytest configuration and fixtures for testing."""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Import all models to ensure they are registered with Base.metadata
# These imports are necessary even though they appear unused
from app.models.book import Book  # noqa: F401
from app.models.review import Review  # noqa: F401
from app.models.user import User  # noqa: F401


# Use Railway PostgreSQL database from environment
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:bnJXOqDDujnWqrkwIJOXwznxlVaLthbo@caboose.proxy.rlwy.net:27901/railway"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session with transaction rollback.

    Uses the Railway PostgreSQL database but rolls back all changes
    after each test to keep the database clean.

    Yields:
        AsyncSession: A test database session
    """
    # Create async engine for Railway PostgreSQL
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create connection and start transaction
    conn = await engine.connect()
    trans = await conn.begin()

    # Create session factory bound to the connection
    async_session_maker = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create session
    session = async_session_maker()

    try:
        yield session
    finally:
        await session.close()
        # Rollback the transaction after test
        await trans.rollback()
        await conn.close()
        await engine.dispose()


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing.

    Args:
        test_db: Test database session

    Yields:
        AsyncClient: An async HTTP client
    """

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
