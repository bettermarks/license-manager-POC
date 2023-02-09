from pydantic import BaseModel, Field


class StatusBase(BaseModel):
    project: str = Field(..., max_length=256)
    version: str = Field(..., max_length=256)
    debug: bool
    description: str = Field(..., max_length=512)


class StatusGet(StatusBase):
    pass
