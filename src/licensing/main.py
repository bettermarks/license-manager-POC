import time
import logging
import uuid

from fastapi import FastAPI


from licensing import __version__ as version
from licensing.logging import ColorFormatter, to_internal_log_level, LogLevel
from licensing.api.api_v1.api import api_router
from licensing.config import settings
from licensing.load_initial_data import load_data, INITIAL_PRODUCTS, INITIAL_HIERARCHY_PROVIDERS

# setup logging
log_level = to_internal_log_level(settings.log_level)
logger = logging.getLogger()
logger.setLevel(log_level)
ch = logging.StreamHandler()
ch.setLevel(log_level)
ch.setFormatter(ColorFormatter())
logger.addHandler(ch)


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

# tha main FastAPI 'app' setup ...
app = FastAPI(
    title="License Manager POC",
    version=version,
    openapi_url=f"/v1/openapi.json",
    debug=True if settings.log_level == LogLevel.DEBUG else False,
    description="A generic license managing application",
    openapi_tags=tags_metadata,
    log_level=log_level
)


@app.middleware("http")
async def log_requests(request, call_next):
    """We are intercepting requests to do some logging."""
    request_id = uuid.uuid4()
    logging.debug(f"request_id={request_id} started request at path={request.url.path}")
    start = time.time()
    response = await call_next(request)
    logging.debug((
        f"request_id={request_id} "
        f"time_used={'{0:.2f}'.format((time.time() - start) * 1000)}ms "
        f"status_code={response.status_code}"
    ))
    return response


@app.on_event("startup")
async def startup():
    # TODO how could initial data be loaded? This seems not to be the right place ...
    await load_data(INITIAL_PRODUCTS)
    await load_data(INITIAL_HIERARCHY_PROVIDERS)


@app.on_event("shutdown")
async def shutdown():
    pass

ROUTE_PREFIX = "/v1"


app.include_router(api_router, prefix="ROUTE_PREFIX")
