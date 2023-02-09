from typing import Any

from fastapi import APIRouter
from fastapi import status as http_status

from licensing.config import settings
from licensing.schema import status as schema

router = APIRouter()


@router.get(
    "/",
    response_model=schema.Status,
    status_code=http_status.HTTP_200_OK
)
def get_status() -> Any:
    return {
        "project": settings.project_name,
        "version": settings.version,
        "debug": settings.debug,
        "description": settings.description
    }
