from fastapi import APIRouter
from fastapi import status as http_status

from licensing.config import settings

router = APIRouter()


@router.get("/", status_code=http_status.HTTP_200_OK)
def get_status():
    return {
        "project": settings.project_name,
        "version": settings.version,
        "debug": settings.debug,
        "description": settings.description
    }
