from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.model import product as model
from licensing.schema.product import ProductGet


async def get_products(session: AsyncSession) -> List[ProductGet]:
    return (
        await session.execute(
            statement=select(
                model.Product
            )
        )
    ).scalars().all()


async def get_product(session: AsyncSession, eid: str) -> ProductGet:
    return (
        await session.execute(
            statement=select(
                model.Product
            ).where(
                model.Product.eid == eid
            )
        )
    ).scalar_one_or_none()


