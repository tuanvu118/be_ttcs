from datetime import datetime, date
from typing import Optional, List

from beanie import PydanticObjectId
from pydantic import BaseModel


class InternalEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    evidence_url: Optional[str] = None
    location: Optional[str] = None
    participant_count: Optional[int] = None
    event_date: Optional[date] = None

class InternalEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    evidence_url: Optional[str] = None
    location: Optional[str] = None
    participant_count: Optional[int] = None
    event_date: Optional[date] = None

class InternalEventRead(BaseModel):
    id: PydanticObjectId
    title: str
    description: Optional[str] = None
    evidence_url: Optional[str] = None
    location: Optional[str] = None
    participant_count: Optional[int] = None
    event_date: Optional[date] = None



class InternalSummary(BaseModel):
    id: PydanticObjectId
    title: str

class UnitEventSummary(BaseModel):
    id: PydanticObjectId
    title: str
    type: str
    created_at: datetime

class ReportBase(BaseModel):
    month: int
    year: int

class ReportSummary(ReportBase):
    unit_id: PydanticObjectId
    semester_id: PydanticObjectId
    id: PydanticObjectId
    status: str
    updated_at: datetime
    total_activities: int = 0


class ReportDetail(ReportBase):
    id: PydanticObjectId
    unit_id: PydanticObjectId
    status: str
    note: Optional[str]
    updated_at: datetime
    unit_events: List[UnitEventSummary] = []
    internal_events: List[InternalEventRead] = []
