import datetime
from typing import List

from pydantic import BaseModel
from licensing.model import product


class LicenseBase(BaseModel):
    start: datetime.date
    end: datetime.date
    seats: int | None


class LicenseCreate(LicenseBase):
    product_eid: str
    owner_hierarchy_level: str
    owner_eids: List[str]


class License(LicenseBase):
    # product: product.Product

    class Config:
        orm_mode = True
