from licm.db import database
from licm.api.models import LicenseSchema
from licm.model import license


async def post(payload: LicenseSchema):
    query = license.License.insert().values(
        title=payload.title, description=payload.description
    )
    return await database.execute(query=query)


async def get(id: int):
    query = license.License.select().where(id == license.license.c.id)
    return await database.fetch_one(query=query)


async def get_all():
    query = license.License.select()
    return await database.fetch_all(query=query)


async def put(id: int, payload: LicenseSchema):
    query = (
        license.License.update()
        .where(id == license.license.c.id)
        .values(title=payload.title, description=payload.description)
        .returning(license.license.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = license.License.delete().where(id == license.license.c.id)
    return await database.execute(query=query)
