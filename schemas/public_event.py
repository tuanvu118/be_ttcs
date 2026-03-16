from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict


class PublicEventBase(BaseModel):
    title: str
    description: str
    image_url: Optional[str] = None
    point: float = 0
    registration_start: datetime
    registration_end: datetime
    event_start: datetime
    event_end: datetime

    auto_add_report: bool = False

class PublicEventCreate(PublicEventBase):
    pass

class PublicEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    point: Optional[float] = None
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    event_start: Optional[datetime] = None
    event_end: Optional[datetime] = None

    auto_add_report: Optional[bool] = None

class PublicEventRead(PublicEventBase):
    id: PydanticObjectId
    semester_id: PydanticObjectId
    created_at: datetime

class PublicEventSummary(BaseModel):
    id: PydanticObjectId
    title: str

    model_config = ConfigDict(from_attributes=True)
