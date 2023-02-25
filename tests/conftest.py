import asyncio
import logging
from typing import Generator

import pytest
import pytest_asyncio

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from licensing.api.api_v1.api import api_router
from licensing.config import settings
from licensing.db import postgres_dsn
from licensing.main import app, ROUTE_PREFIX
from licensing.db import async_session as app_db_session
from tests.integration.initial_data import INITIAL_TEST_PRODUCTS, INITIAL_TEST_HIERARCHY_PROVIDERS

# we need to import all models here to set up the database ...
from licensing.model.hierarchy_provider import HierarchyProvider
from licensing.model.product import Product
from licensing.model.license import License
from licensing.model.seat import Seat
from licensing.model.base import Model


TEST_DATABASE_NAME = "test_licensing"
TEST_DATABASE_DSN = postgres_dsn(
    settings.database_host,
    settings.database_port,
    settings.database_user,
    settings.database_password,
    TEST_DATABASE_NAME
)

# we need that for setting up the DB tables ...
target_metadata = Model.metadata

# redefinition of async_engine for our tests ...
async_test_engine = create_async_engine(TEST_DATABASE_DSN, pool_pre_ping=True, echo=False)
async_test_session_factory = async_sessionmaker(async_test_engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def start_app():
    app = FastAPI()
    app.include_router(api_router, prefix=f"/{ROUTE_PREFIX}")
    return app


@pytest.fixture(scope="session")
async def app() -> FastAPI:
    # Setup:
    logging.debug("Setup ...")
    try:
        # (re)create tables
        async with async_test_engine.begin() as conn:
            await conn.run_sync(target_metadata.drop_all)
            await conn.run_sync(target_metadata.create_all)

        # initial data ...
        async with async_test_session_factory() as s:
            for d in INITIAL_TEST_PRODUCTS + INITIAL_TEST_HIERARCHY_PROVIDERS:
                s.add(d)
                await s.commit()

        yield await start_app()

    finally:
        # Teardown:
        logging.debug("Teardown ...")
        async with async_test_engine.begin() as conn:
            await conn.run_sync(target_metadata.drop_all)


@pytest.fixture(scope="session")
async def async_test_session(app: FastAPI) -> AsyncSession:
    try:
        async with async_test_session_factory() as session:
            yield session
    finally:
        await session.close()


@pytest.fixture(scope="module")
async def async_test_client(app: FastAPI, async_test_session: AsyncSession) -> AsyncClient:
    def session():
        try:
            yield async_test_session
        finally:
            pass

    # Overrides the attached DB session with our nice 'test DEB session'.
    # Now for all tests, the test database is used instead of the 'app database'
    app.dependency_overrides[app_db_session] = session
    async with AsyncClient(app=app, base_url=f"http://test-server/{ROUTE_PREFIX}") as client:
        yield client

    app.dependency_overrides.setdefault
