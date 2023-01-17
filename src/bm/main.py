from fastapi import FastAPI

from bm.api import licenses
from bm.db import database, engine, metadata

metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(licenses.router, prefix="/licenses", tags=["licenses"])
