import pytest

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
from httpx import AsyncClient

from database import get_async_session, Base
from main import app
from auth.models import Base
from core.models import Base


from config import (TEST_DB_HOST, 
                        TEST_DB_USER, 
                        TEST_DB_NAME, 
                        TEST_DB_PASS, 
                        TEST_DB_PORT)


TEST_DATABASE_URL = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

test_async_engine = create_async_engine(url=TEST_DATABASE_URL, poolclass=NullPool)
test_async_session_maker = async_sessionmaker(bind=test_async_engine, class_=AsyncSession)

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session

@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture()
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac