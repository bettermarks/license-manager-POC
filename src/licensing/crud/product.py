from typing import List

from fastapi import status as http_status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.model import product as product_model
from licensing.schema import product as product_schema


async def get_products(session: AsyncSession) -> List[product_schema.Product]:
    """
    gets all available products
    """
    return (
        await session.execute(
            statement=select(
                product_model.Product
            )
        )
    ).scalars().all()


async def get_product(session: AsyncSession, eid: str) -> product_schema.Product:
    """
    gets a product with a given EID or nothing
    """
    return (
        await session.execute(
            statement=select(
                product_model.Product
            ).where(
                product_model.Product.eid == eid
            )
        )
    ).scalar_one_or_none()


async def find_product(session: AsyncSession, eid: str) -> product_model.Product:
    """
    finds a product by a given product EID or raises an HTTPException, if not found.
    """
    product = await get_product(session, eid)
    if not product:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Product with EID='{eid}' not found."
        )
    return product
