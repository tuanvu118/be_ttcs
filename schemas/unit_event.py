from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

from models.unit_event import UnitEventEnum
from beanie import PydanticObjectId
from datetime import datetime
from pydantic import ConfigDict
from schemas.unit import UnitBase, UnitRead

class UnitEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    point: Decimal = Field(default=Decimal("0"))
    type: UnitEventEnum
    semesterId: Optional[PydanticObjectId] = None
    listUnitId: List[PydanticObjectId] = Field(default_factory=list)

class UnitEventResponse(BaseModel):
    id: PydanticObjectId
    title: str
    description: Optional[str] = None
    point: Decimal = Field(default=Decimal("0"))
    type: UnitEventEnum
    semesterId: PydanticObjectId
    created_at: datetime
    created_by: PydanticObjectId
    assigned_units: List[UnitRead]

    model_config = ConfigDict(from_attributes=True)

class UnitEventResponseByUnitId(BaseModel):
    id: PydanticObjectId
    title: str
    description: Optional[str] = None
    point: Decimal = Field(default=Decimal("0"))
    type: UnitEventEnum
    semesterId: PydanticObjectId
    created_at: datetime

class UnitEventUpdate(BaseModel):
    semesterId: Optional[PydanticObjectId] = None
    title: Optional[str] = None
    description: Optional[str] = None
    point: Optional[Decimal] = None
    listUnitId: Optional[List[PydanticObjectId]] = None