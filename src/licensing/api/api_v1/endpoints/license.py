from typing import Any, List

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.crud import license as license_crud
from licensing.crud import seat as seat_crud
from licensing.db import get_async_session
from licensing.schema import license as schema

router = APIRouter()


@router.post("/{purchaser_eid}/purchases", response_model=schema.License, status_code=http_status.HTTP_201_CREATED)
async def purchase_license(
        purchaser_eid: str,
        license_data: schema.LicenseCreate,
        session: AsyncSession = Depends(get_async_session)
) -> Any:
    return await license_crud.purchase(session, purchaser_eid, license_data)


@router.get("/{user_eid}/permissions", status_code=http_status.HTTP_200_OK)
async def get_permissions(
        hierarchy_provider_url: str,
        user_eid: str,
        session: AsyncSession = Depends(get_async_session)
) -> List[Any]:
    return await seat_crud.get_permissions(session, hierarchy_provider_url, user_eid)
