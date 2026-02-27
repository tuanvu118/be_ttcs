from pydantic import BaseModel, Field
from typing import Optional
import decimal
from models.unit_event import UnitEventEnum
from beanie import PydanticObjectId
from datetime import datetime
from pydantic import ConfigDict

class UnitEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    point: decimal.Decimal = Field(default=0, ge=0, le=100)
    type: UnitEventEnum

class UnitEventResponse(BaseModel):
    id: PydanticObjectId
    title: str
    description: Optional[str] = None
    point: decimal.Decimal = Field(default=0, ge=0, le=100)
    type: UnitEventEnum
    created_at: datetime
    created_by: PydanticObjectId

    model_config = ConfigDict(from_attributes=True)