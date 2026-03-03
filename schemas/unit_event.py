from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

from models.unit_event import UnitEventEnum
from beanie import PydanticObjectId
from datetime import datetime
from pydantic import ConfigDict

class UnitEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    point: Decimal = Field(default=Decimal("0"))
    type: UnitEventEnum




class UnitEventResponse(BaseModel):
    id: PydanticObjectId
    title: str
    description: Optional[str] = None
    point: Decimal = Field(default=Decimal("0"))
    type: UnitEventEnum
    created_at: datetime
    created_by: PydanticObjectId

    model_config = ConfigDict(from_attributes=True)