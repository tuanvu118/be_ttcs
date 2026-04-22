from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from decimal import Decimal

from models.unit_event import UnitEventEnum
from beanie import PydanticObjectId
from datetime import datetime, timezone
from pydantic import ConfigDict
from schemas.unit import UnitBase, UnitRead


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class UnitEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    point: Decimal = Field(default=Decimal("0"))
    type: UnitEventEnum
    event_start: datetime
    event_end: datetime
    semesterId: Optional[PydanticObjectId] = None
    listUnitId: List[PydanticObjectId] = Field(default_factory=list)

    @field_validator("event_start", "event_end", mode="before")
    @classmethod
    def normalize_datetimes(cls, value: datetime) -> datetime:
        return _ensure_utc(value)

class UnitEventResponse(BaseModel):
    id: PydanticObjectId
    title: str
    description: Optional[str] = None
    point: Decimal = Field(default=Decimal("0"))
    type: UnitEventEnum
    event_start: Optional[datetime] = None
    event_end: Optional[datetime] = None
    semesterId: PydanticObjectId
    created_at: datetime
    created_by: PydanticObjectId
    assigned_units: List[UnitRead]

    @field_validator("event_start", "event_end", "created_at", mode="before")
    @classmethod
    def normalize_response_datetimes(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return _ensure_utc(value)

    model_config = ConfigDict(from_attributes=True)

class UnitEventResponseByUnitId(BaseModel):
    id: PydanticObjectId
    title: str
    description: Optional[str] = None
    point: Decimal = Field(default=Decimal("0"))
    type: UnitEventEnum
    event_start: Optional[datetime] = None
    event_end: Optional[datetime] = None
    semesterId: PydanticObjectId
    created_at: datetime

    @field_validator("event_start", "event_end", "created_at", mode="before")
    @classmethod
    def normalize_summary_datetimes(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return _ensure_utc(value)

class UnitEventUpdate(BaseModel):
    semesterId: Optional[PydanticObjectId] = None
    title: Optional[str] = None
    description: Optional[str] = None
    point: Optional[Decimal] = None
    event_start: Optional[datetime] = None
    event_end: Optional[datetime] = None
    listUnitId: Optional[List[PydanticObjectId]] = None

    @field_validator("event_start", "event_end", mode="before")
    @classmethod
    def normalize_optional_datetimes(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return _ensure_utc(value)

class UnitEventPaginationResponse(BaseModel):
    items: List[UnitEventResponse]
    total: int
