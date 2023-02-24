import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Generator

import pytest
import pytest_asyncio

from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from licensing.config import settings
from licensing.db import postgres_dsn, DATABASE_URL, get_async_session
from licensing.load_initial_data import INITIAL_PRODUCTS, INITIAL_HIERARCHY_PROVIDERS
from licensing.main import app, ROUTE_PREFIX

INIT_DATABASE_URL = DATABASE_URL  # we will use our standard connection to create and drop the test DB

TEST_DATABASE_NAME = "test_licensing"
TEST_DATABASE_URL = postgres_dsn(
    settings.DATABASE_HOST,
    settings.DATABASE_PORT,
    settings.DATABASE_USER,
    settings.DATABASE_PASSWORD,
    TEST_DATABASE_NAME
)

async_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncSession:
    try:
        async with async_session_factory() as session:
            yield session
    except Exception as ex:
        await session.rollback()
        raise ex
    finally:
        await session.close()

    await async_engine.dispose()


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url=f"http://{ROUTE_PREFIX}") as client:
        yield client


def drop_db(connection):
    logging.debug(f"Dropping Test database '{TEST_DATABASE_NAME}'...")
    connection.execute(text(f"DROP DATABASE {TEST_DATABASE_NAME}"))
    logging.debug(f"Test database '{TEST_DATABASE_NAME}' has been dropped!")


def create_db(connection):
    stmt = text(f"CREATE DATABASE {TEST_DATABASE_NAME}")
    logging.debug(f"Creating Test database '{TEST_DATABASE_NAME}'...")
    try:
        connection.execute(stmt)
    except ProgrammingError as ex:
        drop_db(connection)
        connection.execute(stmt)
    logging.debug(f"Test database '{TEST_DATABASE_NAME}' has been created!")


async def alembic_migrate():
    def execute_upgrade(connection):
        cfg.attributes["connection"] = connection # this injects our test db connection to the alembic script
        command.upgrade(cfg, "head")

    logging.debug("Running alembic migration ...")
    cfg = Config("alembic.ini")
    cfg.set_main_option("script_location", "src/alembic")
    async with async_engine.begin() as c:
        await c.run_sync(execute_upgrade)
    logging.debug("Alembic migrations run.")


async def load_initial_data():
    for d in INITIAL_PRODUCTS + INITIAL_HIERARCHY_PROVIDERS:
        async with async_session_factory() as session:
            session.add(d)
            await session.commit()


@pytest_asyncio.fixture(autouse=True)
async def setup_and_teardown():
    """Fixture to establish 'setup' and 'teardown' code"""

    init_engine = create_async_engine(INIT_DATABASE_URL, isolation_level='AUTOCOMMIT', echo=True)

    # Setup:
    logging.info("Setup ...")
    async with init_engine.connect() as conn:
        await conn.run_sync(create_db)
    await alembic_migrate()
    await load_initial_data()

    yield  # the tests ...

    # Teardown:
    logging.info("Teardown ...")
    #async with init_engine.connect() as conn:
    #    await conn.run_sync(drop_db)


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
