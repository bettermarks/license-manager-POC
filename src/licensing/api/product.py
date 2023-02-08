from fastapi import APIRouter, Depends
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from licensing.db import get_async_session
from licensing.schema import product as schema
from licensing.crud import product as crud

router = APIRouter()


@router.get("/", response_model=List[schema.ProductGet])
async def get_products(session: AsyncSession = Depends(get_async_session)):
    return await crud.get_products(session)


@router.get("/{product_id}", response_model=schema.ProductGet)
async def get_product(product_id, session: AsyncSession = Depends(get_async_session)):
    return await crud.get_product(session, product_id)


