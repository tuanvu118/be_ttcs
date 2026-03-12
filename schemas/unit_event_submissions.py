from pydantic import BaseModel
from beanie import PydanticObjectId
from datetime import datetime
from models.unit_event_submissions import UnitEventSubmissionStatus


class UnitEventSubmissionCreate(BaseModel):
    unitEventId: PydanticObjectId
    unitId: PydanticObjectId
    content: str
    evidenceUrl: str
    status: UnitEventSubmissionStatus

class UnitEventSubmissionResponse(BaseModel):
    unitEventId: PydanticObjectId
    uni
    unitId: PydanticObjectId
    content: str
    evidenceUrl: str
    status: UnitEventSubmissionStatus
    submittedAt: datetime