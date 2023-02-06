from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    eid: str = Field(..., min_length=3, max_length=64)
    name: str = Field(..., min_length=3, max_length=64)
    description: str = Field(..., min_length=3, max_length=256)


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True
