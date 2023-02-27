import json
import re
from typing import Dict, List

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import pytest
from pytest_mock import MockerFixture

from licensing.model import hierarchy_provider as hierarchy_provider_model
from licensing.model import product as product_model
from licensing.model import license as license_model



@pytest.fixture
def teacher_1_purchase_payload(
        product_1: product_model.Product,
        hierarchy_provider_1: hierarchy_provider_model.HierarchyProvider,
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


@pytest.mark.asyncio
async def test_purchase_license__422_product(client: AsyncClient, teacher_1, teacher_1_purchase_payload):
    """
    Requested product is not registered
    """
    payload = teacher_1_purchase_payload
    payload["product_eid"] = "product_that_does_not_exist"
    response = await client.post(f"/users/{teacher_1.eid}/purchases", json=payload)
    assert response.status_code == 422
    assert json.loads(response._content) == {
        "detail": f"""License creation failed: product with EID '{payload["product_eid"]}' cannot be not found."""
    }


@pytest.mark.asyncio
async def test_purchase_license__422_hierarchy_provider(client: AsyncClient, teacher_1, teacher_1_purchase_payload):
    """
    Requested hierarchy provider is not registered
    """
    payload = teacher_1_purchase_payload
    payload["hierarchy_provider_url"] = "http://not_existing_hierarchy_provider.com/hierarchy"
    response = await client.post(f"/users/{teacher_1.eid}/purchases", json=payload)
    assert response.status_code == 422
    assert json.loads(response._content) == {
        "detail": (
            f"""License creation failed: Hierarchy provider with base URL="""
            f"""'{payload["hierarchy_provider_url"]}' is not registered."""
        )
    }


@pytest.mark.asyncio
async def test_purchase_license__500_hierarchy_provider(
        mocker: MockerFixture, client: AsyncClient, teacher_1, teacher_1_purchase_payload
):
    """
    Hierarchy provider is down
    """
    mocker.patch(
        "licensing.crud.hierarchy_provider.http_get",
        side_effect=Exception
    )
    payload = teacher_1_purchase_payload
    response = await client.post(f"/users/{teacher_1.eid}/purchases", json=payload)
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_purchase_license__422_not_matching_owner(
        client: AsyncClient,
        session: AsyncSession,
        teacher_no_class_2,
        class_2,
        teacher_1_purchase_payload,
        mock_get_hierarchy_provider_membership
):
    """
    License cannot be purchased, because purchasing teacher is not membership of given owner class
    """
    payload = teacher_1_purchase_payload
    response = await client.post(f"/users/{teacher_no_class_2.eid}/purchases", json=payload)
    assert response.status_code == 422
    assert json.loads(response._content) == {
        "detail": (
            f"License creation failed: license owner ('{class_2.eid}') does not match any users membership."
        )
    }


@pytest.mark.asyncio
async def test_purchase_license__ok(
        client: AsyncClient,
        session: AsyncSession,
        teacher_1,
        teacher_1_purchase_payload,
        mock_get_hierarchy_provider_membership
):
    """
    Yes, purchase a license!
    """
    payload = teacher_1_purchase_payload
    response = await client.post(f"/users/{teacher_1.eid}/purchases", json=payload)
    license_uuid = json.loads(response._content)["license_uuid"]

    # ok. we should have a lciense in the DB!
    #lic = (
    #    await session.execute(
    #        select(license_model.License).where(license_model.License.uuid == license_uuid))
    #).scalar_one_or_none()
    #print("license = ", lic)

    #print("license_uuid = ", license_uuid)
    assert response.status_code == 201

    # TODO to be continued ....

