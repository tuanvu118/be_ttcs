from datetime import datetime
from typing import Optional, List

from beanie import PydanticObjectId
from pydantic import BaseModel

from schemas.public_event import PublicEventSummary


class InternalEventCreate(BaseModel):
    title: str
    description: str
    evidence_url: Optional[str] = None
    location: Optional[str] = None
    participant_count: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class InternalEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    evidence_url: Optional[str] = None
    location: Optional[str] = None
    participant_count: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class InternalEventRead(BaseModel):
    id: PydanticObjectId
    title: str
    description: Optional[str]
    evidence_url: Optional[str]
    location: Optional[str]
    participant_count: Optional[int]
    start_time: Optional[datetime]
    end_time: Optional[datetime]



class InternalSummary(BaseModel):
    id: PydanticObjectId
    title: str

class ReportBase(BaseModel):
    month: int
    year: int

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    month: Optional[int] = None
    year: Optional[int] = None

class ReportSummary(ReportBase):
    unit_id: PydanticObjectId
    id: PydanticObjectId


class ReportDetail(ReportBase):
    id: PydanticObjectId
    unit_id: PydanticObjectId
    public_events: List[PublicEventSummary]
    internal_events: List[InternalSummary]


