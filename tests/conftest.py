import asyncio

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from httpx import AsyncClient

from licensing.main import app


@pytest.fixture(scope="session")
def postgres_engine():
    engine = create_async_engine(
        "postgresql://scott:tiger@127.0.0.1:5432/test"
    )
    yield engine
    engine.sync_engine.dispose()


@pytest.fixture
async def session(engine):
    async with AsyncSession(engine) as session:
        yield session


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
            app=app,
            base_url=f"http://v1"
    ) as client:
        yield client
