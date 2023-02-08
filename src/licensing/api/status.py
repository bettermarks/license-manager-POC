from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_status():
    return "OK"