from typing import Any

from fastapi import APIRouter
from fastapi import status as http_status

from licensing.config import settings
from licensing.logging import LogLevel

router = APIRouter()


@router.get("/", status_code=http_status.HTTP_200_OK)
def get_status() -> Any:
    return {
        "status": "OK",
        "debug": True if settings.log_level == LogLevel.DEBUG else False,
    }
