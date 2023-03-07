import time
import structlog

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
from fastapi import FastAPI, Request, Response
from uvicorn.protocols.utils import get_path_with_query_string

from licensing import settings
from licensing import __version__ as version
from licensing.logging import setup_logging, LogLevel
from licensing.api.api_v1.api import api_router
from licensing.load_initial_data import (
    load_data,
    INITIAL_PRODUCTS,
    INITIAL_HIERARCHY_PROVIDERS,
)


setup_logging(settings.log_format, settings.log_level)
access_logger = structlog.stdlib.get_logger("api.access")
logger = structlog.stdlib.get_logger(__name__)


# some metadata for our API (will be nicely printed out via /docs)
tags_metadata = [
    {
        "name": "Licenses",
        "description": (
            "Purchasing and redeeming operations for licenses. A license is basically "
            "a 'relation' between a product and one or more 'license owners' with "
            "some constraints like a start date, an end date and a number of open "
            "'seats'."
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
        "description": ("The API status and other useful (debug) information"),
    },
]

app = FastAPI(
    title="Licensing Service",
    version=version,
    openapi_url="/v1/openapi.json",
    debug=True if settings.log_level == LogLevel.DEBUG else False,
    description="A generic license managing application",
    openapi_tags=tags_metadata,
)


# TODO: do we need request logs?
@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    structlog.contextvars.clear_contextvars()
    # These context vars will be added to all log entries emitted during the request
    request_id = correlation_id.get()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start_time = time.perf_counter_ns()

    # If the call_next raises an error, we still want to return our own 500 response,
    # so we can add headers to it (process time, request ID...)
    response = Response(status_code=500)
    try:
        response = await call_next(request)
    except Exception:
        # TODO: Validate that we don't swallow exceptions (unit test?)
        structlog.stdlib.get_logger("api.error").exception("Uncaught exception")
        raise
    finally:
        process_time = time.perf_counter_ns() - start_time
        status_code = response.status_code
        url = get_path_with_query_string(request.scope)
        client_host = request.client.host
        client_port = request.client.port
        http_method = request.method
        http_version = request.scope["http_version"]
        # Recreate the Uvicorn access log format, but add all parameters as structured
        # information. Ignore status calls
        if not request.app.url_path_for("get_status") in request.url.path:
            access_logger.info(
                f'{client_host}:{client_port} - "{http_method} {url} '
                f'HTTP/{http_version}" {status_code}',
                http={
                    "url": str(request.url),
                    "status_code": status_code,
                    "method": http_method,
                    "request_id": request_id,
                },
                network={"client": {"ip": client_host, "port": client_port}},
                duration=process_time,
            )
        # response.headers["X-Process-Time"] = str(process_time / 10**9)
        return response


# This middleware must be placed after the logging, to populate the context with the
# request ID
# NOTE: Why last??
# Answer: middlewares are applied in the reverse order of when they are added (you can
# verify this by debugging `app.middleware_stack` and recursively drilling down the
# `app` property).
app.add_middleware(CorrelationIdMiddleware)


# add application performance monitoring middleware
apm = make_apm_client(
    {
        "SERVICE_NAME": f"licensing-{settings.segment}",
        "SECRET_TOKEN": settings.apm_secret_token,
        "SERVER_URL": settings.apm_url,
        "ENVIRONMENT": settings.segment,
        "TRANSACTIONS_IGNORE_PATTERNS": ["^OPTIONS", "/v1/status"],
        "ENABLED": settings.apm_enabled,
        "SERVICE_VERSION": version,
        "TRANSACTION_SAMPLE_RATE": settings.apm_transaction_sample_rate,
        "COLLECT_LOCAL_VARIABLES": True,  # TODO: check
    }
)
app.add_middleware(ElasticAPM, client=apm)


@app.on_event("startup")
async def startup():
    # TODO how could initial data be loaded? This seems not to be the right place ...
    await load_data(INITIAL_PRODUCTS)
    await load_data(INITIAL_HIERARCHY_PROVIDERS)


@app.on_event("shutdown")
async def shutdown():
    pass


ROUTE_PREFIX = "/v1"


app.include_router(api_router, prefix=ROUTE_PREFIX)
