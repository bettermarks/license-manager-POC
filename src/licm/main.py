import logging
from fastapi import FastAPI

from licm.api import product

# init logging
logging.basicConfig(format="%(levelname)s:\t%(message)s", level=logging.INFO)

app = FastAPI()


@app.on_event("startup")
async def startup():
    # TODO
    pass


@app.on_event("shutdown")
async def shutdown():
    # TODO
    pass


app.include_router(product.router, prefix="/products", tags=["products"])
