from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(from_attributes=True)

class UnitEventRegistrationResponse(BaseModel):
    id: PydanticObjectId
    event_id: PydanticObjectId
    user_id: PydanticObjectId
    unit_id: PydanticObjectId
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EventRegistrationUserResponse(BaseModel):
    user_id: PydanticObjectId
    full_name: str
    student_id: str
    answers: List[FormAnswer] = Field(default_factory=list)
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MyEventRegistrationResponse(BaseModel):
    event_id: PydanticObjectId
    title: str
    event_start: datetime
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MyEventDetailResponse(BaseModel):
    event_id: PydanticObjectId
    title: str
    description: str
    event_start: datetime
    event_end: datetime
    answers: Optional[List["FormAnswer"]] = Field(default=None)
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)
