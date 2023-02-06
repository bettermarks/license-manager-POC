import logging
from fastapi import FastAPI

from licensing.api import product, status
from licensing.load_initial_data import load_initial_products, load_initial_hierarchy_providers

# init logging
logging.basicConfig(format="%(levelname)s:\t%(message)s", level=logging.INFO)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await load_initial_products()
    await load_initial_hierarchy_providers()


@app.on_event("shutdown")
async def shutdown():
    # TODO
    pass


app.include_router(product.router, prefix="/products", tags=["products"])
app.include_router(status.router, prefix="/status", tags=["debug"])
