import datetime

from pydantic import BaseModel, Field


class SeatBase(BaseModel):
    user_eid: str = Field(min_length=1, max_length=256, default="30001048769")  # TODO remove default


class SeatCreate(SeatBase):
    pass


class Seat(SeatBase):
    ref_license: int
    occupied: datetime.datetime
    released: datetime.datetime
    last_login: datetime.datetime
    is_occupied: bool

    class Config:
        orm_mode = True


