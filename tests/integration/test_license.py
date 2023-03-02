import json

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import selectinload

from licensing.model import license as license_model


@pytest.mark.asyncio
async def test_purchase_license__422_product(
    client: AsyncClient, teacher_1, teacher_1_purchase_payload
):
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
async def test_purchase_license__422_hierarchy_provider(
    client: AsyncClient, teacher_1, teacher_1_purchase_payload
):
    """
    Requested hierarchy provider is not registered
    """
    payload = teacher_1_purchase_payload
    payload[
        "hierarchy_provider_url"
    ] = "http://not_existing_hierarchy_provider.com/hierarchy"
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
    mocker.patch("licensing.crud.hierarchy_provider.http_get", side_effect=Exception)
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
    mock_get_hierarchy_provider_membership,
):
    """
    License cannot be purchased, because purchasing teacher is not membership of given owner class
    """
    payload = teacher_1_purchase_payload
    response = await client.post(
        f"/users/{teacher_no_class_2.eid}/purchases", json=payload
    )
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
    mock_get_hierarchy_provider_membership,
):
    """
    Yes, purchase a license!
    """
    payload = teacher_1_purchase_payload
    response = await client.post(f"/users/{teacher_1.eid}/purchases", json=payload)
    license_uuid = json.loads(response._content)["license_uuid"]

    # ok. we should have a license in the DB!
    licenses = (
        (
            await session.execute(
                select(license_model.License)
                .where(license_model.License.uuid == license_uuid)
                .order_by(license_model.License.owner_eid)
                .options(  # we need that as async does not support lazy loading!
                    selectinload(license_model.License.product)
                )
                .options(  # we need that as async does not support lazy loading!
                    selectinload(license_model.License.hierarchy_provider)
                )
            )
        )
        .scalars()
        .all()
    )

    assert response.status_code == 201
    assert len(licenses) == 2
    assert {
        "owner_type": licenses[0].owner_type,
        "owner_eids": [l.owner_eid for l in licenses],
        "valid_from": licenses[0].valid_from.strftime("%Y-%m-%d"),
        "valid_to": licenses[0].valid_to.strftime("%Y-%m-%d"),
        "seats": licenses[0].seats,
        "hierarchy_provider_url": licenses[0].hierarchy_provider.url,
        "product_eid": licenses[0].product.eid,
    } == teacher_1_purchase_payload


@pytest.mark.asyncio
async def test_purchase_license__409_license_purchased_twice(
    client: AsyncClient,
    session: AsyncSession,
    teacher_1,
    teacher_1_purchase_payload,
    mock_get_hierarchy_provider_membership,
):
    """
    Try to purchase the same license twice
    """
    payload = teacher_1_purchase_payload
    response = await client.post(f"/users/{teacher_1.eid}/purchases", json=payload)
    assert response.status_code == 201
    response = await client.post(f"/users/{teacher_1.eid}/purchases", json=payload)
    assert response.status_code == 409
    assert json.loads(response._content) == {
        "detail": (
            f"License creation failed: A license for at least one of the owner "
            f"EIDs'({teacher_1_purchase_payload['owner_eids']})"
            f"({teacher_1_purchase_payload['owner_type']})', valid from "
            f"'{teacher_1_purchase_payload['valid_from']}' to "
            f"'{teacher_1_purchase_payload['valid_to']}' already has been created."
        )
    }
