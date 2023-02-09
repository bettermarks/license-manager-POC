from typing import List

from fastapi import status as http_status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from licensing.crud.hierarchy_provider import get_hierarchy_provider
from licensing.crud.product import get_product
from licensing.model import hierarchy_provider as hierarchy_provider_model
from licensing.model import product as product_model
from licensing.model import license as license_model
from licensing.schema import license as license_schema


async def find_product(session: AsyncSession, product_eid: str) -> product_model.Product:
    """
    finds a product by a given product EID or raises an HTTPException
    """
    product = await get_product(session, product_eid)
    if not product:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Product with EID='{product_eid}' not found."
        )
    return product


async def find_hierarchy_provider(session: AsyncSession, url: str) -> hierarchy_provider_model.HierarchyProvider:
    """
    checks, if the provided hierarchy provider exists or raises an HTTPException
    """
    provider = await get_hierarchy_provider(session, url)
    if not provider:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Hierarchy provider with base URL='{url}' not registered."
        )
    return provider


async def check_owners(session: AsyncSession, owner_eids: List[str]) -> hierarchy_provider_model.HierarchyProvider:
    """
    checks, if the requested license owners are in the 'hierarchy path' of the pruchaser.
    That means: is the purchaser 'allowed' to purchase a license for the given owners?
    This is true, if and only if the purchaser is 'member' of the license owner, f.e.
    some class or some school.
    Raises an HTTPException on failure
    """
    product = await get_product(session, product_eid)
    if not product:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Product with EID='{product_eid}' not found. License purchase failed."
        )
    return product


async def purchase_license(
        session: AsyncSession, purchaser_eid: str, license_data: license_schema.LicenseCreate
) -> license_model.License:

    # 0. check, if requesting user is purchaser
    # TODO

    # 1. find product
    product = await find_product(session, license_data.product_eid)

    # 2. create license
    lic = license_model.License(
        ref_product=product.id,
        purchaser_eid=purchaser_eid,
        **{k: v for k, v in license_data if k != "product_eid"}
    )
    session.add(lic)
    await session.commit()
    return lic
