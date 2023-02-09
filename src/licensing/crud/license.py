from fastapi import status as http_status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from licensing.crud.product import get_product
from licensing.model import license as model
from licensing.schema import license as schema


async def purchase_license(
        session: AsyncSession, purchaser_eid: str, license_data: schema.LicenseCreate
) -> model.License:

    # 1. find product
    product = await get_product(session, license_data.product_eid)
    if not product:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Product with EID='{license_data.product_eid}' not found. License purchase failed."
        )

    # 2. create license
    lic = model.License(
        ref_product=product.id,
        purchaser_eid=purchaser_eid,
        **{k: v for k, v in license_data if k != "product_eid"}
    )
    session.add(lic)
    await session.commit()
    return lic
