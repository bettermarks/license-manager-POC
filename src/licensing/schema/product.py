from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    eid: str = Field(..., min_length=3, max_length=256)
    name: str = Field(..., min_length=3, max_length=256)
    description: str = Field(..., max_length=512)


class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True
