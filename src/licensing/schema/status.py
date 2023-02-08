from pydantic import BaseModel, Field


class StatusBase(BaseModel):
    project: str
    version: str
    debug: bool
    description: str


class StatusGet(StatusBase):
    pass
