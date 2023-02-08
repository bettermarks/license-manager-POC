from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.model import product as model


async def get_products(session: AsyncSession):
    return (await session.execute(select(model.Product))).scalars().all()


async def get_product(session: AsyncSession, eid: str):
    return (await session.execute(select(model.Product).where(model.Product.eid == eid))).scalar()


