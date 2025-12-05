"""
Test configuration and fixtures for FastAPI backend tests.
Uses SQLite in-memory database for isolation and speed.
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from app.database import Base, get_db
from app.main import app


# Use SQLite in-memory for tests (no MySQL dependency)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create tables and yield a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with overridden DB dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_session_data():
    """Sample data for creating a session."""
    return {
        "language": "python",
        "code": "print('Hello, World!')"
    }


@pytest.fixture
def sample_code_update():
    """Sample data for code update."""
    return {
        "code": "def main():\n    print('Updated code')"
    }


@pytest.fixture
def sample_language_update():
    """Sample data for language update."""
    return {
        "language": "javascript"
    }
