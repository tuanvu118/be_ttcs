from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict


class UnitBase(BaseModel):
    name: str
    logo: Optional[str] = None
    introduction: Optional[str] = None
    type: Optional[str] = None


class UnitCreate(UnitBase):
    name: str
    type: Optional[str] = None


class UnitUpdate(BaseModel):
    name: Optional[str] = None
    introduction: Optional[str] = None
    type: Optional[str] = None


class UnitRead(UnitBase):
    id: PydanticObjectId

    model_config = ConfigDict(from_attributes=True)


class UnitListResponse(BaseModel):
    items: list[UnitRead]
    total: int
    skip: int
    limit: int
