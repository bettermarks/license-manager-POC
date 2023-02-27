import json
import re

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def teacher_1_eid() -> str:
    return "teacher_1"


@pytest.fixture
def student_1_eid() -> str:
    return "student_1"


@pytest.fixture
def student_2_eid() -> str:
    return "student_2"


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


async def http_get_hierarchy_provider_membership(url: str, payload: dict | None = None):
    user_eid = re.findall('\w+/users/(\w+)/membership', url)[0]

    match user_eid:
        case "teacher_1":
            return [
                {"type": "class", "level": 1, "eid": "class_1"},
                {"type": "class", "level": 1, "eid": "class_2"},
            ]
        case "student_1":
            return [
                {"type": "class", "level": 1, "eid": "class_1"},
            ]
        case "student_2":
            return [
                {"type": "class", "level": 1, "eid": "class_2"},
            ]


@pytest.mark.asyncio
async def test_purchase_license__422_product(
        client: AsyncClient,
        teacher_1_eid,
        purchase_payload: dict
):
    """
    Requested product is not registered
    """
    payload = purchase_payload
    payload["product_eid"] = "does_not_exist"
    response = await client.post(f"/users/{teacher_1_eid}/purchases", json=payload)
    assert response.status_code == 422
    assert json.loads(response._content) == {
        "detail": f"""License creation failed: product with EID '{payload["product_eid"]}' cannot be not found."""
    }


@pytest.mark.asyncio
async def test_purchase_license__422_hierarchy_provider(
        client: AsyncClient,
        teacher_1_eid,
        purchase_payload: dict
):
    """
    Requested hierarchy provider is not registered
    """
    payload = purchase_payload
    payload["hierarchy_provider_url"] = "http://illegal_hierarchy_provider.com/hierarchy"
    response = await client.post(f"/users/{teacher_1_eid}/purchases", json=payload)
    assert response.status_code == 422
    assert json.loads(response._content) == {
        "detail": (
            f"""License creation failed: Hierarchy provider with base URL="""
            f"""'{payload["hierarchy_provider_url"]}' is not registered."""
        )
    }


@pytest.mark.asyncio
async def test_purchase_license__500_hierarchy_provider(
        mocker: MockerFixture,
        client: AsyncClient,
        teacher_1_eid,
        purchase_payload: dict
):
    """
    Hierarchy provider is down
    """
    mocker.patch(
        "licensing.crud.hierarchy_provider.http_get",
        side_effect=Exception
    )
    payload = purchase_payload
    response = await client.post(f"/users/{teacher_1_eid}/purchases", json=payload)
    print("response._content = ", response._content)
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_purchase_license__ok(
        mocker: MockerFixture,
        client: AsyncClient,
        session: AsyncSession,
        teacher_1_eid,
        purchase_payload: dict
):
    """
    Yes, purchase a license!
    """
    mocker.patch("licensing.crud.hierarchy_provider.http_get", side_effect=http_get_hierarchy_provider_membership)
    payload = purchase_payload
    response = await client.post(f"/users/{teacher_1_eid}/purchases", json=payload)
    print("response._content = ", response._content)
    assert response.status_code == 201

