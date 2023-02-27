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
def teacher_no_class_1_eid() -> str:
    return "teacher_no_class_1"


@pytest.fixture
def student_1_eid() -> str:
    return "student_1"


@pytest.fixture
def student_2_eid() -> str:
    return "student_2"


@pytest.fixture
def class_1_eid() -> str:
    return "class_1"


@pytest.fixture
def class_2_eid() -> str:
    return "class_2"


@pytest.fixture
def purchase_payload(product_1, hierarchy_provider_1, class_1_eid, class_2_eid) -> dict:
    return {
        "owner_type": "class",
        "owner_eids": [
            class_1_eid,
            class_2_eid
        ],
        "valid_from": "2023-02-10",
        "valid_to": "2024-02-10",
        "seats": 100,
        "hierarchy_provider_url": hierarchy_provider_1.url,
        "product_eid": product_1.eid
    }


async def http_get_hierarchy_provider_membership(url: str, payload: dict | None = None):
    # like www.my-hierarchy-provider.de/users/{some user_eid}/membership
    user_eid = re.findall('\w+/users/(\w+)/membership', url)[0]

    match user_eid:
        case "teacher_1":
            return [
                {"type": "class", "level": 1, "eid": "class_1"},
                {"type": "class", "level": 1, "eid": "class_2"},
            ]
        case "teacher_no_class_1":   # a teacher that is not member of 'class_1'
            return [
                {"type": "class", "level": 1, "eid": "class_3"},
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
    payload["product_eid"] = "product_that_does_not_exist"
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
    payload["hierarchy_provider_url"] = "http://not_existing_hierarchy_provider.com/hierarchy"
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
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_purchase_license__422_not_matching_owner(
        mocker: MockerFixture,
        client: AsyncClient,
        session: AsyncSession,
        teacher_no_class_1_eid,
        class_1_eid,
        purchase_payload: dict
):
    """
    License cannot be purchased, because purchasing teacher is not membership of given owner class
    """
    mocker.patch("licensing.crud.hierarchy_provider.http_get", side_effect=http_get_hierarchy_provider_membership)
    payload = purchase_payload
    response = await client.post(f"/users/{teacher_no_class_1_eid}/purchases", json=payload)
    assert response.status_code == 422
    assert json.loads(response._content) == {
        "detail": (
            f"License creation failed: license owner ('{class_1_eid}') does not match any users membership."
        )
    }


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

    # TODO to be continued ....
