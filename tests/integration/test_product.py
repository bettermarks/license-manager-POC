import json
from dataclasses import asdict

import pytest
from httpx import AsyncClient

from tests.integration.initial_data import INITIAL_TEST_PRODUCTS


@pytest.mark.asyncio
async def test_get_products(async_test_client: AsyncClient):
    response = await async_test_client.get("/products/")
    assert response.status_code == 200

    data = json.loads(response._content)
    print("products")
    print([asdict(p) for p in INITIAL_TEST_PRODUCTS])

    assert data == [asdict(p) for p in INITIAL_TEST_PRODUCTS]

