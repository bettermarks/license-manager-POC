import datetime
from typing import List

from pydantic import BaseModel, validator


class LicenseBase(BaseModel):
    product_eid: str
    owner_hierarchy_level: str
    owner_eids: List[str]
    start: datetime.date
    end: datetime.date
    seats: int | None


class LicenseCreate(LicenseBase):
    pass


class License(LicenseBase):
    id: int

    class Config:
        orm_mode = True
