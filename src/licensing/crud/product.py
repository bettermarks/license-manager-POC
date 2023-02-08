from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.model import product as model
from licensing.schema.product import ProductGet


async def get_products(session: AsyncSession):
    return (await session.execute(select(model.Product))).scalars().all()


async def get_product(session: AsyncSession, eid: str) -> ProductGet:
    statement = select(
        model.Product
    ).where(
        model.Product.eid == eid
    )
    return (await session.execute(statement=statement)).scalar_one_or_none()


