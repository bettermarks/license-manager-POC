from fastapi import status as http_status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from licensing.crud.product import get_product
from licensing.model import product as product_model
from licensing.model import license as license_model
from licensing.schema import license as license_schema


async def find_product(session: AsyncSession, product_eid: str) -> product_model.Product:
    """finds a product by a given product EID or raises an HTTPException"""
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
