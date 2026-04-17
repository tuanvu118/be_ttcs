from datetime import datetime, timezone
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator


class FormAnswer(BaseModel):
    field_id: str
    value: str

class EventRegistrationRequest(BaseModel):
    answers: List[FormAnswer] = Field(default_factory=list)

class EventRegistrationResponse(BaseModel):
    id: PydanticObjectId
    event_id: PydanticObjectId
    user_id: PydanticObjectId
    answers: List[FormAnswer] = Field(default_factory=list)
    registered_at: datetime

    @field_validator("registered_at", mode="before", check_fields=False)
    @classmethod
    def force_utc(cls, v):
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    model_config = ConfigDict(from_attributes=True)

class UnitEventRegistrationResponse(BaseModel):
    id: PydanticObjectId
    event_id: PydanticObjectId
    user_id: PydanticObjectId
    unit_id: PydanticObjectId
    registered_at: datetime

    @field_validator("registered_at", mode="before", check_fields=False)
    @classmethod
    def force_utc(cls, v):
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    model_config = ConfigDict(from_attributes=True)

class EventRegistrationUserResponse(BaseModel):
    user_id: PydanticObjectId
    full_name: str
    student_id: str
    answers: List[FormAnswer] = Field(default_factory=list)
    registered_at: datetime

    @field_validator("registered_at", mode="before", check_fields=False)
    @classmethod
    def force_utc(cls, v):
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    model_config = ConfigDict(from_attributes=True)


class MyEventRegistrationResponse(BaseModel):
    event_id: PydanticObjectId
    title: str
    event_start: datetime
    registered_at: datetime

    @field_validator("registered_at", "event_start", mode="before", check_fields=False)
    @classmethod
    def force_utc(cls, v):
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    model_config = ConfigDict(from_attributes=True)


class MyEventDetailResponse(BaseModel):
    event_id: PydanticObjectId
    title: str
    description: str
    image_url: Optional[str] = None
    point: float = 0
    location: Optional[str] = None
    max_participants: int = 0
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    event_start: datetime
    event_end: datetime
    form_fields: List[dict] = Field(default_factory=list)
    answers: Optional[List["FormAnswer"]] = Field(default=None)
    registered_at: datetime

    @field_validator("registration_start", "registration_end", "event_start", "event_end", "registered_at", mode="before", check_fields=False)
    @classmethod
    def force_utc(cls, v):
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    model_config = ConfigDict(from_attributes=True)
