from repositories.unit_event_submissions_repo import UnitEventSubmissionsRepo
from repositories.unit_event_submission_members_repo import UnitEventSubmissionMembersRepo
from schemas.unit_event_submissions import (
    UnitEventSubmissionCreate,
    UnitEventSubmissionResponse,
    UnitEventSubmissionUpdate,
    UnitEventSubmissionMemberCreate,
    UnitEventSubmissionMemberResponse,
)
from models.unit_event_submissions import UnitEventSubmission, UnitEventSubmissionStatus
from models.unit_event import UnitEvent
from models.unit_event_submission_members import UnitEventSubmissionMember
from exceptions import ErrorCode, app_exception
from models.unit_event import UnitEventEnum
from beanie import PydanticObjectId
from datetime import datetime

class UnitEventSubmissionsService:
    def __init__(
        self,
        repo: UnitEventSubmissionsRepo,
        unit_event_submission_members_repo: UnitEventSubmissionMembersRepo | None = None,
    ):
        self.repo = repo
        self.unit_event_submission_members_repo = (
            unit_event_submission_members_repo or UnitEventSubmissionMembersRepo()
        )
    def _parse_object_id(self, value: PydanticObjectId | str, field_name: str) -> PydanticObjectId:
        try:
            return PydanticObjectId(str(value))
        except Exception:
            app_exception(
                ErrorCode.INVALID_ID_FORMAT,
                extra_detail=f"{field_name} không đúng định dạng",
            )

    async def _build_submission_member_response(
        self, submission: UnitEventSubmission
    ) -> UnitEventSubmissionMemberResponse:
        members = await self.unit_event_submission_members_repo.get_all_by_unit_event_submission_id(
            submission.id
        )
        list_user_id = [member.userId for member in members]
        return UnitEventSubmissionMemberResponse(
            unitEventId=submission.unitEventId,
            unitId=submission.unitId,
            content=submission.content or "",
            evidenceUrl=submission.evidenceUrl or "",
            status=submission.status,
            submittedAt=submission.submittedAt,
            list_user_id=list_user_id,
        )

    async def create_unit_event_submission(self, data: UnitEventSubmissionCreate, current_user: str) -> UnitEventSubmissionResponse:
        unit_event_id = self._parse_object_id(data.unitEventId, "unitEventId")
        unit_event = await UnitEvent.get(unit_event_id)
        if not unit_event:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        if unit_event.type != UnitEventEnum.HTTT:
            app_exception(ErrorCode.INVALID_UNIT_EVENT_TYPE_VALUE)
        existing_submission = await self.repo.get_by_unit_event_id_and_unit_id(unit_event_id, data.unitId)
        if existing_submission:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_ALREADY_EXISTS)
        unit_event_submission = UnitEventSubmission(
            unitEventId=unit_event_id,
            unitId=self._parse_object_id(data.unitId, "unitId"),
            content=data.content,
            evidenceUrl=data.evidenceUrl,
            submittedAt=datetime.now(),
        )
        saved = await self.repo.create(unit_event_submission)
        return UnitEventSubmissionResponse.model_validate(saved)
    
    async def get_unit_event_submissions_by_unit_event_id(
        self, unit_event_id: PydanticObjectId | str, unit_id: PydanticObjectId | str
    ) -> UnitEventSubmissionResponse:
        parsed_unit_event_id = self._parse_object_id(unit_event_id, "unit_event_id")
        parsed_unit_id = self._parse_object_id(unit_id, "unit_id")
        submission = await self.repo.get_by_unit_event_id_and_unit_id(
            parsed_unit_event_id, parsed_unit_id
        )
        if not submission:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_NOT_FOUND)
        return UnitEventSubmissionResponse.model_validate(submission)

    async def update_unit_event_submission(
        self,
        unit_event_id: PydanticObjectId | str,
        unit_id: PydanticObjectId | str,
        data: UnitEventSubmissionUpdate,
    ) -> UnitEventSubmissionResponse:
        parsed_unit_event_id = self._parse_object_id(unit_event_id, "unit_event_id")
        parsed_unit_id = self._parse_object_id(unit_id, "unit_id")

        submission = await self.repo.get_by_unit_event_id_and_unit_id(
            parsed_unit_event_id, parsed_unit_id
        )
        if not submission:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_NOT_FOUND)

        if submission.status == UnitEventSubmissionStatus.APPROVED:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_ALREADY_APPROVED)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(submission, field, value)
        if submission.status == UnitEventSubmissionStatus.REJECTED:
            submission.status = UnitEventSubmissionStatus.PENDING
        submission.submittedAt = datetime.now()

        saved = await self.repo.update(submission)
        return UnitEventSubmissionResponse.model_validate(saved)


    async def create_unit_event_submission_member(
        self, data: UnitEventSubmissionMemberCreate, x_unit_id: str
    ) -> UnitEventSubmissionMemberResponse:
        unit_event_id = self._parse_object_id(data.unitEventId, "unitEventId")
        unit_event = await UnitEvent.get(unit_event_id)
        if not unit_event:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        if unit_event.type != UnitEventEnum.HTSK:
            app_exception(ErrorCode.INVALID_UNIT_EVENT_TYPE_VALUE)
        unit_id = self._parse_object_id(x_unit_id, "x_unit_id")
        existing_submission = await self.repo.get_by_unit_event_id_and_unit_id(unit_event_id, unit_id)
        if existing_submission:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_ALREADY_EXISTS)
        if data.list_user_id is None:
            app_exception(ErrorCode.LIST_USER_ID_IS_REQUIRED)
        unit_event_submission = UnitEventSubmission(
            unitEventId=unit_event_id,
            unitId=unit_id,
            content=data.content,
            evidenceUrl=data.evidenceUrl,
            submittedAt=datetime.now(),
        )
        saved = await self.repo.create(unit_event_submission)

        for user_id in data.list_user_id:
            unit_event_submission_member = UnitEventSubmissionMember(
                unitEventSubmissionId=saved.id,
                userId=user_id,
                checkIn=False,
            )
            await self.unit_event_submission_members_repo.create(unit_event_submission_member)

        return await self._build_submission_member_response(saved)


    async def get_unit_event_submissions_HTSK_by_unit_event_id(
        self, unit_event_id: PydanticObjectId | str, x_unit_id: str
    ) -> UnitEventSubmissionMemberResponse:
        parsed_unit_event_id = self._parse_object_id(unit_event_id, "unit_event_id")
        parsed_unit_id = self._parse_object_id(x_unit_id, "x_unit_id")
        submission = await self.repo.get_by_unit_event_id_and_unit_id(parsed_unit_event_id, parsed_unit_id)
        if not submission:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_NOT_FOUND)
        return await self._build_submission_member_response(submission)