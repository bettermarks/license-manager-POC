from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from licensing.db import get_async_session
from licensing.schema import product as schema
from licensing.crud import product as crud

router = APIRouter()


@router.get(
    "/",
    response_model=List[schema.Product],
    status_code=http_status.HTTP_200_OK
)
async def get_products(session: AsyncSession = Depends(get_async_session)) -> Any:
    """this is a comment"""
    return await crud.get_products(session)


@router.get(
    "/{product_eid}",
    response_model=schema.Product,
    status_code=http_status.HTTP_200_OK
)
async def get_product(product_eid, session: AsyncSession = Depends(get_async_session)) -> Any:
    product = await crud.get_product(session, product_eid)
    if product is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="The product could not be found."
        )
    return product
