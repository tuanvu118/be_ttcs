from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId
from datetime import datetime
from models.unit_event_submissions import UnitEventSubmissionStatus
from typing import List


class UnitEventSubmissionCreate(BaseModel):
    unitEventId: PydanticObjectId
    unitId: PydanticObjectId
    content: str
    evidenceUrl: str

class UnitEventSubmissionResponse(BaseModel):
    unitEventId: PydanticObjectId
    unitId: PydanticObjectId
    content: str
    evidenceUrl: str
    status: UnitEventSubmissionStatus
    submittedAt: datetime

    model_config = ConfigDict(from_attributes=True)


class UnitEventSubmissionUpdate(BaseModel):
    content: str | None = None
    evidenceUrl: str | None = None


class UnitEventSubmissionMemberCreate(BaseModel):
    unitEventId: PydanticObjectId
    unitId: PydanticObjectId
    content: str
    evidenceUrl: str | None = None
    list_user_id: List[PydanticObjectId] | None = None


class UnitEventSubmissionMemberResponse(BaseModel):
    unitEventId: PydanticObjectId
    unitId: PydanticObjectId
    content: str
    evidenceUrl: str
    status: UnitEventSubmissionStatus
    submittedAt: datetime
    list_user_id: List[PydanticObjectId]

    model_config = ConfigDict(from_attributes=True)

