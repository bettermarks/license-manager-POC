from fastapi import HTTPException, APIRouter

from licm.db import get_session
from licm.schema import product as schema
from licm.crud import product as crud

router = APIRouter()


@router.post("/", response_model=schema.Product, status_code=201)
async def create_product(product: schema.ProductCreate):
    async with get_session() as session:
        existing_product = await crud.get_product(session,  eid=product.eid)
        print('existing_product =', existing_product)
        if existing_product:
            raise HTTPException(status_code=400, detail="Product already registered")
        return await crud.create_product(session, product=product)
