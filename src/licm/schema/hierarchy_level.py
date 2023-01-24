from pydantic import BaseModel, Field


class HierarchyLevelBase(BaseModel):
    level: int
    name: str = Field(..., min_length=3, max_length=256)
    description: str = Field(..., min_length=3, max_length=50)


class HierarchyLevelCreate(HierarchyLevelBase):
    pass


class HierarchyLevel(HierarchyLevelBase):
    id: int
    ref_hierarchy_provider: int

    class Config:
        orm_mode = True

