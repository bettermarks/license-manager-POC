from pydantic import BaseModel, Field


class HierarchyProviderBase(BaseModel):
    eid: str = Field(..., min_length=3, max_length=64)
    name: str = Field(..., min_length=3, max_length=64)
    description: str = Field(..., min_length=3, max_length=256)
    hierarchy_url: str = Field(..., min_length=3, max_length=256)


class HierarchyProviderCreate(HierarchyProviderBase):
    pass


class HierarchyProvider(HierarchyProviderBase):
    id: int

    class Config:
        orm_mode = True
