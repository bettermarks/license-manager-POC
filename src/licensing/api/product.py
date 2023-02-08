from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from licensing.db import get_async_session
from licensing.schema import product as schema
from licensing.crud import product as crud

router = APIRouter()


@router.get("/", response_model=List[schema.ProductGet], status_code=http_status.HTTP_200_OK)
async def get_products(session: AsyncSession = Depends(get_async_session)):
    """this is a comment"""
    return await crud.get_products(session)


@router.get("/{product_id}", response_model=schema.ProductGet, status_code=http_status.HTTP_200_OK)
async def get_product(product_id, session: AsyncSession = Depends(get_async_session)):
    product = await crud.get_product(session, product_id)
    if product is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="The product could not be found."
        )
    return product
