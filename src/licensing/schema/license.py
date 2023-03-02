import datetime
from typing import List

from pydantic import BaseModel, Field, constr, HttpUrl


class LicenseBase(BaseModel):
    owner_type: str = Field(
        min_length=1, max_length=256, default="class"
    )  # TODO remove default
    owner_eids: List[constr(min_length=1, max_length=256)] = [
        "50000154044",
        "50000158191",
    ]  # TODO remove this default
    valid_from: datetime.date = datetime.date(2023, 2, 10)  # TODO remove this default
    valid_to: datetime.date = datetime.date(2024, 2, 10)  # TODO remove this default
    seats: int | None = 100  # TODO remove this default


class LicenseCreate(LicenseBase):
    hierarchy_provider_url: HttpUrl = (
        "http://0.0.0.0:5001/hierarchy"  # TODO remove this default
    )
    product_eid: str = Field(
        default="full_access", min_length=1, max_length=256
    )  # TODO remove this default


class License(LicenseBase):
    ref_product: int

    class Config:
        orm_mode = True
