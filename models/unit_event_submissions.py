from beanie import Document, PydanticObjectId
from datetime import datetime
from enum import Enum

class UnitEventSubmissionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class UnitEventSubmission(Document):
    unitEventId: PydanticObjectId
    unitId: PydanticObjectId

    content: str
    evidenceUrl: str
    status: UnitEventSubmissionStatus
    submittedAt: datetime

    class Settings:
        name = "unit_event_submissions"