from beanie import Document, PydanticObjectId, DecimalAnnotation
from pydantic import Field
from decimal import Decimal

from datetime import datetime
from typing import Optional
from enum import Enum


class UnitEventEnum(str, Enum):
    HTTT = "HTTT"
    HTSK = "HTSK"


class UnitEvent(Document):
    title: str
    description: Optional[str] = None
    point: DecimalAnnotation = Field(
        default=Decimal("0"),
        ge=Decimal("0"),
        le=Decimal("10"),
    )
    type: UnitEventEnum
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: PydanticObjectId

    class Settings:
        name = "unit_events"