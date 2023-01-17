from typing import List

from fastapi import APIRouter, HTTPException, Path

from bm.api import crud
from bm.api.models import LicenseDB, LicenseSchema

router = APIRouter()


@router.post("/", response_model=LicenseDB, status_code=201)
async def create_license(payload: LicenseSchema):
    license_id = await crud.post(payload)

    response_object = {
        "id": license_id,
        "title": payload.title,
        "description": payload.description,
    }
    return response_object


@router.get("/{id}/", response_model=LicenseDB)
async def read_license(
    id: int = Path(..., gt=0),
):
    license = await crud.get(id)
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
    return license


@router.get("/", response_model=List[LicenseDB])
async def read_all_license():
    return await crud.get_all()


@router.put("/{id}/", response_model=LicenseDB)
async def update_license(
    payload: LicenseSchema,
    id: int = Path(..., gt=0),
):
    license = await crud.get(id)
    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    license_id = await crud.put(id, payload)

    response_object = {
        "id": license_id,
        "title": payload.title,
        "description": payload.description,
    }
    return response_object


@router.delete("/{id}/", response_model=LicenseDB)
async def delete_license(id: int = Path(..., gt=0)):
    license = await crud.get(id)
    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    await crud.delete(id)

    return license
