import datetime

from pydantic import BaseModel, Field


class SeatBase(BaseModel):
    user_eid: str = Field(
        min_length=1, max_length=256, default="30001048769"
    )  # TODO remove default


class SeatCreate(SeatBase):
    pass


class Seat(SeatBase):
    ref_license: int
    occupied_at: datetime.datetime
    released_at: datetime.datetime
    last_login: datetime.datetime
    is_occupied: bool

    class Config:
        orm_mode = True
