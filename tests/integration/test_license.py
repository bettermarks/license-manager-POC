import json

import aiohttp
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def purchase_payload() -> dict:
    return {
        "owner_type": "class",
        "owner_eids": [
            "class_1",
            "class_2"
        ],
        "valid_from": "2023-02-10",
        "valid_to": "2024-02-10",
        "seats": 100,
        "hierarchy_provider_url": "http://mocked_hierarchy_provider.com/hierarchy",
        "product_eid": "full_access"
    }


@pytest.mark.asyncio
async def test_purchase_license__422_product(client: AsyncClient, session: AsyncSession, purchase_payload: dict):
    purchaser_eid = "teacher_1"
    payload = purchase_payload
    payload["product_eid"] = "does_not_exist"

    response = await client.post(f"/users/{purchaser_eid}/purchases", json=payload)

    assert response.status_code == 422
    assert json.loads(response._content) == {
        "detail": f"""License creation failed: product with EID '{payload["product_eid"]}' cannot be not found."""
    }


@pytest.mark.asyncio
async def test_purchase_license__404_hierarchy_provider(
        client: AsyncClient, session: AsyncSession, purchase_payload: dict
):
    purchaser_eid = "teacher_1"
    payload = purchase_payload
    payload["hierarchy_provider_url"] = "http://illegal_hierarchy_provider.com/hierarchy"

    response = await client.post(f"/users/{purchaser_eid}/purchases", json=payload)

    assert response.status_code == 422
    assert json.loads(response._content) == {
        "detail": (
            f"""License creation failed: Hierarchy provider with base URL="""
            f"""'{payload["hierarchy_provider_url"]}' is not registered."""
        )
    }


@pytest.mark.asyncio
async def test_purchase_license__500_hierarchy_provider(
        mocker: MockerFixture, client: AsyncClient, session: AsyncSession, purchase_payload: dict
):
    mocker.patch("licensing.http_client.http_get", side_effect=[aiohttp.client_exceptions.ClientConnectorError])
    purchaser_eid = "teacher_1"
    payload = purchase_payload
    response = await client.post(f"/users/{purchaser_eid}/purchases", json=payload)
    assert response.status_code == 500


#    print("response._content ", response._content)
