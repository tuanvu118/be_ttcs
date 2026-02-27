from beanie import Document, PydanticObjectId
from pydantic import Field
import decimal
from datetime import datetime
from typing import Optional
from enum import Enum

class UnitEventEnum(str, Enum):
    HTTT = "HTTT"
    HTSK = "HTSK"

class UnitEvent(Document):
    title: str
    description: Optional[str] = None
    point: decimal.Decimal = Field(default=0, ge=0, le=100)
    type: UnitEventEnum
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: PydanticObjectId

    class Settings:
        name = "unit_events"