from pydantic import AliasChoices, BaseModel, ConfigDict, Field, computed_field
from beanie import PydanticObjectId
from datetime import datetime
from models.unit_event_submissions import UnitEventSubmissionStatus
from typing import List, Union
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
    list_MSV: List[str] | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "list_MSV", "list_msv", "listMsv", "list_user_id", "listUserId"
        ),
    )


class UnitEventSubmissionMemberUpdate(BaseModel):
    content: str | None = None
    evidenceUrl: str | None = None
    list_MSV: List[str] | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "list_MSV", "list_msv", "listMsv", "list_user_id", "listUserId"
        ),
    )


class UnitEventSubmissionMemberResponse(BaseModel):
    unitEventId: PydanticObjectId
    unitId: PydanticObjectId
    content: str
    evidenceUrl: str
    status: UnitEventSubmissionStatus
    submittedAt: datetime
    list_user_id: List[Union[PydanticObjectId, str]]

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def list_MSV(self) -> List[str]:
        """Trùng dữ liệu với list_user_id (MSV hoặc id), tiện cho client đọc một key thống nhất."""
        return [str(x) for x in self.list_user_id]


class UnitEventSubmissionWithUnitResponse(BaseModel):
    id: PydanticObjectId
    unitEventId: PydanticObjectId
    unit: UnitBase
    content: str
    evidenceUrl: str
    status: UnitEventSubmissionStatus
    submittedAt: datetime

