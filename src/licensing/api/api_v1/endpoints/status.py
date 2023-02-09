from typing import Any

from fastapi import APIRouter
from fastapi import status as http_status

from licensing.config import settings
from licensing.schema import status as status_schema

router = APIRouter()


@router.get(
    "/",
    response_model=status_schema.Status,
    status_code=http_status.HTTP_200_OK
)
def get_status() -> Any:
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "debug": settings.DEBUG,
        "description": settings.DESCRIPTION
    }
