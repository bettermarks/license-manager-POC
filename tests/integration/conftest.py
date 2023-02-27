import asyncio
import logging
import re
from dataclasses import dataclass

from typing import Generator, List, Dict

import pytest

from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from licensing.api.api_v1.api import api_router
from licensing.config import settings
from licensing.db import postgres_dsn
from licensing.main import app, ROUTE_PREFIX
from licensing.db import async_session as app_db_session

# we need to import all models here to set up the database ...
from licensing.model.hierarchy_provider import HierarchyProvider
from licensing.model.product import Product
from licensing.model.license import License  # Please do not remove that import!!
from licensing.model.seat import Seat  # Please do not remove that import!!
from licensing.model.base import Model


@dataclass
class User:
    eid: str
    level: int = 0


class Teacher(User):
    type_: str = "teacher"


class Student(User):
    type_: str = "student"


@dataclass
class Class_:
    eid: str
    type_: str = "class"
    level: int = 1


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


@pytest.fixture
def teacher_1() -> Teacher:
    return Teacher(eid="teacher_1")


@pytest.fixture
def teacher_no_class_2() -> Teacher:
    return Teacher(eid="teacher_no_class_2")


@pytest.fixture
def student_1() -> Student:
    return Student(eid="student_1")


@pytest.fixture
def student_2() -> Student:
    return Student(eid="student_2")


@pytest.fixture
def class_1() -> Class_:
    return Class_(eid="class_1")


@pytest.fixture
def class_2() -> Class_:
    return Class_(eid="class_2")


@pytest.fixture
def class_3() -> Class_:
    return Class_(eid="class_3")


@pytest.fixture(scope="session")
def product_1() -> Product:
    return Product(
        eid="full_access",
        name="full access for all bettermarks content",
        description="This product gives full access to all bettermarks books",
        permissions=[{"*": "rx"}]
    )


@pytest.fixture(scope="session")
def hierarchy_provider_1() -> HierarchyProvider:
    return HierarchyProvider(
        url="http://mocked_hierarchy_provider.com/hierarchy",
        short_name="a mocked hierarchy provider",
        name="some mocked hierarchy provider",
        description="This is some mocked hierarchy provider"
    )


@pytest.fixture(scope="session")
def products(product_1) -> List[Product]:
    return [product_1]


@pytest.fixture(scope="session")
def hierarchy_providers(hierarchy_provider_1) -> List[HierarchyProvider]:
    return [hierarchy_provider_1]


@pytest.fixture
def teacher_1_purchase_payload(
        product_1: Product,
        hierarchy_provider_1: HierarchyProvider,
        class_1,
        class_2
) -> dict:
    return {
        "owner_type": class_1.type_,
        "owner_eids": [
            class_1.eid,
            class_2.eid
        ],
        "valid_from": "2023-02-10",
        "valid_to": "2024-02-10",
        "seats": 100,
        "hierarchy_provider_url": hierarchy_provider_1.url,
        "product_eid": product_1.eid
    }


@pytest.fixture()
async def mock_get_hierarchy_provider_membership(
        mocker: MockerFixture, class_1, class_2, class_3, teacher_1, teacher_no_class_2, student_1, student_2
) -> List[Dict[str, str | int]]:
    """ this is our mocked 'hierarchy-provider-membership service'"""
    async def _http_get(url: str, payload: dict | None = None):
        # like www.my-hierarchy-provider.de/users/{some user_eid}/membership
        user_eid = re.findall('\w+/users/(\w+)/membership', url)[0]

        match user_eid:
            case teacher_1.eid:
                return [
                    {"type": class_1.type_, "level": class_1.level, "eid": class_1.eid},
                    {"type": class_2.type_, "level": class_2.level, "eid": class_2.eid},
                ]
            case teacher_no_class_2.eid:   # a teacher that is not member of 'class_1'
                return [
                    {"type": class_1.type_, "level": class_1.level, "eid": class_1.eid},
                    {"type": class_3.type_, "level": class_3.level, "eid": class_3.eid},
                ]
            case student_1.eid:
                return [
                    {"type": class_1.type_, "level": class_1.level, "eid": class_1.eid},
                ]
            case student_2.eid:
                return [
                    {"type": class_2.type_, "level": class_2.level, "eid": class_2.eid},
                ]

    mocker.patch("licensing.crud.hierarchy_provider.http_get", side_effect=_http_get)


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
async def app(products, hierarchy_providers) -> FastAPI:
    # Setup:
    logging.debug("Setup ...")
    try:
        # (re)create tables
        async with async_test_engine.begin() as conn:
            await conn.run_sync(target_metadata.drop_all)
            await conn.run_sync(target_metadata.create_all)

        # initial data ...
        async with async_test_session_factory() as s:
            for d in products + hierarchy_providers:
                s.add(d)
                await s.commit()

        yield await start_app()

    finally:
        # Teardown:
        logging.debug("Teardown ...")
        async with async_test_engine.begin() as conn:
            await conn.run_sync(target_metadata.drop_all)


@pytest.fixture(scope="session")
async def session(app: FastAPI) -> AsyncSession:
    try:
        async with async_test_session_factory() as session:
            yield session
    finally:
        await session.close()


@pytest.fixture(scope="module")
async def client(app: FastAPI, session: AsyncSession) -> AsyncClient:
    def _session():
        yield session

    # Overrides the attached DB session with our nice 'test DB session'.
    # Now for all tests, the test database is used instead of the 'app database'
    app.dependency_overrides[app_db_session] = _session
    async with AsyncClient(app=app, base_url=f"http://test-server/{ROUTE_PREFIX}") as client:
        yield client

    app.dependency_overrides.setdefault

