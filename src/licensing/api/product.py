from fastapi import APIRouter
from typing import List

from licensing.db import get_session
from licensing.schema import product as schema
from licensing.crud import product as crud

router = APIRouter()


@router.post("/", response_model=schema.Product, status_code=201)
async def create_product(product: schema.ProductCreate):
    async with get_session() as session:
        return await crud.create_product(session, product=product)
        # raise HTTPException(status_code=400, detail="Product already registered")


@router.get("/{product_id}", response_model=schema.Product)
async def get_product(product_id):
    async with get_session() as session:
        return await crud.get_product(session, product_id)


@router.get("/", response_model=List[schema.Product])
async def get_products():
    async with get_session() as session:
        return await crud.get_products(session)
