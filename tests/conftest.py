import asyncio
import logging
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
from licensing.db import postgres_dsn, DATABASE_DSN
from licensing.main import app, ROUTE_PREFIX
from licensing.db import async_session as app_db_session
from tests.integration.initial_data import INITIAL_TEST_PRODUCTS, INITIAL_TEST_HIERARCHY_PROVIDERS

INIT_DATABASE_DSN = DATABASE_DSN  # we will use our standard connection to create and drop the test DB

TEST_DATABASE_NAME = "test_licensing"
TEST_DATABASE_DSN = postgres_dsn(
    settings.database_host,
    settings.database_port,
    settings.database_user,
    settings.database_password,
    TEST_DATABASE_NAME
)

# redefinition of async_engine for our tests ...
async_test_engine = create_async_engine(TEST_DATABASE_DSN, echo=False)
async_test_session_factory = async_sessionmaker(async_test_engine, expire_on_commit=False)


async def async_test_session() -> AsyncSession:
    """Redefinition of async_session for our tests ..."""
    try:
        async with async_test_session_factory() as session:
            yield session
    except Exception as ex:
        await session.rollback()
        raise ex
    finally:
        await session.close()


# Overrides the attached DB session with our nice 'test DEB session'.
# Now for all tests, the test database is used instead of the 'app database'
app.dependency_overrides[app_db_session] = async_test_session


@pytest_asyncio.fixture
async def async_test_client():
    """This is our 'test http client'"""
    async with AsyncClient(app=app, base_url=f"http://test-server/{ROUTE_PREFIX}") as client:
        yield client


def drop_db(connection):
    """Drops the test database on setup (if it exists) and on teardown"""
    connection.execute(text(f"DROP DATABASE {TEST_DATABASE_NAME}"))


def create_db(connection):
    """Creates the test database on setup"""
    stmt = text(f"CREATE DATABASE {TEST_DATABASE_NAME}")
    try:
        connection.execute(stmt)
    except ProgrammingError as ex:
        drop_db(connection)
        connection.execute(stmt)


async def alembic_migrate():
    """Performs all alembic migrations in our test database"""
    def execute_upgrade(connection):
        cfg.attributes["connection"] = connection  # this injects our test db connection to the alembic env script
        command.upgrade(cfg, "head")

    cfg = Config("alembic.ini")
    cfg.set_main_option("script_location", "src/alembic")
    async with async_test_engine.begin() as c:
        await c.run_sync(execute_upgrade)


async def load_initial_data():
    """Loads initial data into our test database ..."""
    for d in INITIAL_TEST_PRODUCTS + INITIAL_TEST_HIERARCHY_PROVIDERS:
        async with async_test_session_factory() as session:
            session.add(d)
            await session.commit()


@pytest_asyncio.fixture(autouse=True)
async def setup_and_teardown():
    """Fixture to establish 'setup' and 'teardown' code"""

    init_engine = create_async_engine(INIT_DATABASE_DSN, isolation_level='AUTOCOMMIT', echo=True)

    # Setup:
    logging.debug("Setup ...")
    async with init_engine.connect() as conn:
        await conn.run_sync(create_db)
    await alembic_migrate()
    await load_initial_data()

    yield  # the tests ...

    # Teardown:
    logging.debug("Teardown ...")
    # async with init_engine.connect() as conn:
    #    await conn.run_sync(drop_db)


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

