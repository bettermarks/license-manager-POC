import logging
from fastapi import FastAPI

from licensing.api import license, product, status
from licensing.config import settings
from licensing.load_initial_data import load_initial_products, load_initial_hierarchy_providers

# init logging
logging.basicConfig(format="%(levelname)s:\t%(message)s", level=logging.INFO)

# some metadata for our API (will be nicely printed out via /docs)
tags_metadata = [
    {
        "name": "Licenses",
        "description": (
            "Purchasing and redeeming operations for licenses. A license is basically a "
            "'relation' between a product and one or more 'license owners' with some constraints "
            "like a start date, an end date and a number of open 'seats'."
        ),
    },
    {
        "name": "Products",
        "description": (
            "Operations with products. A product is basically something, "
            "a user can purchase."
        ),
    },
    {
        "name": "Debug",
        "description": (
            "The API status and other useful (debug) information"
        ),
    },
]

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_version_prefix}/openapi.json",
    debug=settings.debug,
    openapi_tags=tags_metadata
)


@app.on_event("startup")
async def startup():
    # TODO how could initial data be loaded? This seems not to be the right place ...
    await load_initial_products()
    await load_initial_hierarchy_providers()


@app.on_event("shutdown")
async def shutdown():
    pass


app.include_router(license.router, prefix="/licenses", tags=["Licenses"])
app.include_router(product.router, prefix="/products", tags=["Products"])
app.include_router(status.router, prefix="/status", tags=["Debug"])
