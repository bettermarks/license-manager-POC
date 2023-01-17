from bm.api.models import LicenseSchema
from bm.db import licenses, database


async def post(payload: LicenseSchema):
    query = licenses.insert().values(
        title=payload.title, description=payload.description
    )
    return await database.execute(query=query)


async def get(id: int):
    query = licenses.select().where(id == licenses.c.id)
    return await database.fetch_one(query=query)


async def get_all():
    query = licenses.select()
    return await database.fetch_all(query=query)


async def put(id: int, payload: LicenseSchema):
    query = (
        licenses.update()
        .where(id == licenses.c.id)
        .values(title=payload.title, description=payload.description)
        .returning(licenses.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = licenses.delete().where(id == licenses.c.id)
    return await database.execute(query=query)
