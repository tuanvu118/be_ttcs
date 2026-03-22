from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId
from datetime import datetime
from models.unit_event_submissions import UnitEventSubmissionStatus
from typing import List
from schemas.unit import UnitBase


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


class UnitEventSubmissionStatusUpdate(BaseModel):
    unit_event_submission_id: PydanticObjectId
    status: UnitEventSubmissionStatus


class UnitEventSubmissionMemberCreate(BaseModel):
    unitEventId: PydanticObjectId
    unitId: PydanticObjectId
    content: str
    list_MSV: List[str] | None = None


class UnitEventSubmissionMemberUpdate(BaseModel):
    content: str | None = None
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


class UnitEventSubmissionWithUnitResponse(BaseModel):
    id: PydanticObjectId
    unitEventId: PydanticObjectId
    unit: UnitBase
    content: str
    evidenceUrl: str
    status: UnitEventSubmissionStatus
    submittedAt: datetime

