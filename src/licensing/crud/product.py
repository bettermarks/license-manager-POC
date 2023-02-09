from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.model import product as product_model
from licensing.schema import product as product_schema


async def get_products(session: AsyncSession) -> List[product_schema.Product]:
    return (
        await session.execute(
            statement=select(
                product_model.Product
            )
        )
    ).scalars().all()


async def get_product(session: AsyncSession, eid: str) -> product_schema.Product:
    return (
        await session.execute(
            statement=select(
                product_model.Product
            ).where(
                product_model.Product.eid == eid
            )
        )
    ).scalar_one_or_none()


