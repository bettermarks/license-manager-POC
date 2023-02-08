from fastapi import APIRouter
from fastapi import status as http_status

from licensing.config import settings
from licensing.schema.status import Status

router = APIRouter()


@router.get("/", response_model=Status, status_code=http_status.HTTP_200_OK)
def get_status():
    return {
        "project": settings.project_name,
        "version": settings.version,
        "debug": settings.debug,
        "description": settings.description
    }
