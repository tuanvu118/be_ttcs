from datetime import datetime
from typing import Optional, List

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict


from models.public_event import EventFormField


class PublicEventBase(BaseModel):
    title: str
    description: str
    image_url: Optional[str] = None
    point: float = 0

    registration_start: datetime
    registration_end: datetime

    event_start: datetime
    event_end: datetime
    location: Optional[str] = None
    max_participants: int = 0



    form_fields: List[EventFormField] = []


class PublicEventCreate(PublicEventBase):
    semester_id: Optional[PydanticObjectId] = None


class PublicEventUpdate(BaseModel):
    semester_id: Optional[PydanticObjectId] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    point: Optional[float] = None

    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None

    event_start: Optional[datetime] = None
    event_end: Optional[datetime] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None

    form_fields: Optional[List[EventFormField]] = None


class PublicEventRead(PublicEventBase):
    id: PydanticObjectId
    semester_id: PydanticObjectId
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicEventSummary(BaseModel):
    id: PydanticObjectId
    title: str
    event_start: Optional[datetime] = None
    location: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
