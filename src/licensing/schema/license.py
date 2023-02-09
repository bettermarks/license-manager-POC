import datetime
from typing import List

from pydantic import BaseModel, Field, constr


class LicenseBase(BaseModel):
    owner_hierarchy_level: str = Field(..., min_length=1, max_length=256)
    owner_eids: List[constr(min_length=1, max_length=256)]
    start: datetime.date
    end: datetime.date
    seats: int | None


class LicenseCreate(LicenseBase):
    product_eid: str = Field(..., min_length=1, max_length=256)


class License(LicenseBase):
    ref_product: int

    class Config:
        orm_mode = True
