from fastapi import APIRouter, Depends
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.db import get_async_session
from licensing.schema import license as schema
from licensing.crud import license as crud

router = APIRouter()


@router.post(
    "/{purchaser_eid}/purchase",
    response_model=schema.License,
    status_code=http_status.HTTP_201_CREATED
)
async def purchase_license(
        purchaser_eid: str,
        license_data: schema.LicenseCreate,
        session: AsyncSession = Depends(get_async_session)
):
    return await crud.purchase_license(session, purchaser_eid, license_data)

