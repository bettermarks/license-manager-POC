from typing import List

from fastapi import status as http_status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.model import product as model
from licensing.schema import product as schema


async def get_products(session: AsyncSession) -> List[schema.Product]:
    """
    gets all available products
    """
    return (
        await session.execute(statement=select(model.Product))
    ).scalars().all()


async def get_product(session: AsyncSession, eid: str) -> schema.Product:
    """
    gets a product with a given EID or nothing
    """
    return (
        await session.execute(statement=select(model.Product).where(model.Product.eid == eid))
    ).scalar_one_or_none()
