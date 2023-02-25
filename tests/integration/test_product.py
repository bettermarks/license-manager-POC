import json
from dataclasses import asdict

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.schema import product as schema
from licensing.model import product as model
from tests.integration.initial_data import INITIAL_TEST_PRODUCTS


@pytest.mark.asyncio
async def test_get_products__ok(async_test_client: AsyncClient):
    response = await async_test_client.get("/products/")
    assert response.status_code == 200
    assert json.loads(response._content) == [asdict(schema.Product.from_orm(p)) for p in INITIAL_TEST_PRODUCTS]


@pytest.mark.asyncio
async def test_get_product__ok(async_test_client: AsyncClient, async_test_session: AsyncSession):
    eid = "full_access"
    response = await async_test_client.get(f"/products/{eid}")
    assert response.status_code == 200
    product = (await async_test_session.execute(
        select(model.Product).where(model.Product.eid == eid))
    ).scalar_one_or_none()
    assert json.loads(response._content) == asdict(schema.Product.from_orm(product))


@pytest.mark.asyncio
async def test_get_product__404(async_test_client: AsyncClient, async_test_session: AsyncSession):
    eid = "something"
    response = await async_test_client.get(f"/products/{eid}")
    assert response.status_code == 404
    assert json.loads(response._content) == {'detail': 'The product could not be found.'}
