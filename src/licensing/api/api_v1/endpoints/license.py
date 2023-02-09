from typing import Any

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.db import get_async_session
from licensing.schema import license as license_schema
from licensing.crud import license as license_crud

router = APIRouter()


@router.post(
    "/{purchaser_eid}/purchases",
    response_model=license_schema.License,
    status_code=http_status.HTTP_201_CREATED
)
async def purchase_license(
        purchaser_eid: str,
        license_data: license_schema.LicenseCreate,
        session: AsyncSession = Depends(get_async_session)
) -> Any:
    return await license_crud.purchase_license(session, purchaser_eid, license_data)


@router.get(
    "/{user_eid}/permissions",
    response_model=license_schema.License,
    status_code=http_status.HTTP_200_OK
)
async def get_permissions(user_eid: str, session: AsyncSession = Depends(get_async_session)) -> Any:
    return await license_crud.get_permissions(session, user_eid)
