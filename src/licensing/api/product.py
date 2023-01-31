from fastapi import HTTPException, APIRouter

from licensing.db import get_session
from licensing.schema import product as schema
from licensing.crud import product as crud

router = APIRouter()


@router.post("/", response_model=schema.Product, status_code=201)
async def create_product(product: schema.ProductCreate):
    async with get_session() as session:
        return await crud.create_product(session, product=product)
        # raise HTTPException(status_code=400, detail="Product already registered")
