import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_products(async_client: AsyncClient, async_session: AsyncSession):
    response = await async_client.get("/products")
    assert response.status_code == 200

    results = await async_session.execute(statement=text("SELECT * from product"))
    print("results = ", results)
    assert 1 == 0

