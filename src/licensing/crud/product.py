from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from licensing.model import product as model
from licensing.schema import product as schema


async def get_product(session: AsyncSession, eid: str):
    return (await session.execute(select(model.Product).where(model.Product.eid == eid))).scalar()


async def get_products(session: AsyncSession):
    return (await session.execute(select(model.Product))).scalars().all()


async def create_product(session: AsyncSession, product: schema.Product):
    new_product = model.Product(eid=product.eid, name=product.name, description=product.description)
    session.add(new_product)
    await session.flush()
    return new_product
