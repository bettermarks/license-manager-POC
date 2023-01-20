import logging
from fastapi import FastAPI

from licm.api import licenses
from licm.db import database, engine, metadata

# init logging
logging.basicConfig(format="%(levelname)s:\t%(message)s", level=logging.INFO)

# create Tables etc. from SQLAlchemy Table etc. definitions
# metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(licenses.router, prefix="/licenses", tags=["licenses"])
