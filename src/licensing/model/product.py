from sqlmodel import Field

from licensing.model.base import Model


class Product(Model, table=True):
    eid: str = Field(max_length=256, nullable=False, index=True, sa_column_kwargs={"unique": True})
    name: str = Field(max_length=256, nullable=False, index=True)
    description: str = Field(max_length=256)


