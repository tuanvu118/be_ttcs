from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

from models.unit_event import UnitEventEnum
from beanie import PydanticObjectId
from datetime import datetime
from pydantic import ConfigDict
from schemas.unit import UnitBase

class UnitEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    point: Decimal = Field(default=Decimal("0"))
    type: UnitEventEnum
    assigned_units: List[PydanticObjectId]

class UnitEventResponse(BaseModel):
    id: PydanticObjectId
    title: str
    description: Optional[str] = None
    point: Decimal = Field(default=Decimal("0"))
    type: UnitEventEnum
    created_at: datetime
    created_by: PydanticObjectId
    assigned_units: List[UnitBase]

    model_config = ConfigDict(from_attributes=True)

class UnitEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    point: Optional[Decimal] = None
    assigned_units: Optional[List[PydanticObjectId]] = None