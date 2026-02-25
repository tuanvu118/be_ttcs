from datetime import datetime
from typing import List, Optional
from beanie import Document, PydanticObjectId
from pydantic import Field, BaseModel


class InternalEvent(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    title: str
    description: Optional[str] = None
    evidence_url: Optional[str] = None
    location: Optional[str] = None
    participant_count: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class Report(Document):
    unit_id: PydanticObjectId
    month: int
    year: int

    public_event_ids: List[PydanticObjectId] = Field(default_factory=list)
    internal_events: List[InternalEvent] = Field(default_factory=list)

    class Settings:
        name = "reports"
