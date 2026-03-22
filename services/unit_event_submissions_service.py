from repositories.unit_event_submissions_repo import UnitEventSubmissionsRepo
from repositories.unit_event_submission_members_repo import UnitEventSubmissionMembersRepo
from repositories.unit_repo import UnitRepo
from schemas.unit_event_submissions import (
    UnitEventSubmissionCreate,
    UnitEventSubmissionResponse,
    UnitEventSubmissionUpdate,
    UnitEventSubmissionStatusUpdate,
    UnitEventSubmissionMemberCreate,
    UnitEventSubmissionMemberUpdate,
    UnitEventSubmissionMemberResponse,
    UnitEventSubmissionWithUnitResponse,
)
from models.unit_event_submissions import UnitEventSubmission, UnitEventSubmissionStatus
from models.unit_event import UnitEvent
from models.unit_event_submission_members import UnitEventSubmissionMember
from exceptions import ErrorCode, app_exception
from models.unit_event import UnitEventEnum
from beanie import PydanticObjectId
from datetime import datetime
from schemas.unit import UnitBase
from typing import List

class UnitEventSubmissionsService:
    def __init__(
        self,
        repo: UnitEventSubmissionsRepo,
        unit_event_submission_members_repo: UnitEventSubmissionMembersRepo | None = None,
        unit_repo: UnitRepo | None = None,
    ):
        self.repo = repo
        self.unit_event_submission_members_repo = (
            unit_event_submission_members_repo or UnitEventSubmissionMembersRepo()
        )
        self.unit_repo = unit_repo or UnitRepo()
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

    async def get_all_httt_submissions_by_unit_event_id(
        self, unit_event_id: PydanticObjectId | str
    ) -> List[UnitEventSubmissionWithUnitResponse]:
        parsed_unit_event_id = self._parse_object_id(unit_event_id, "unit_event_id")
        unit_event = await UnitEvent.get(parsed_unit_event_id)
        if not unit_event:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        if unit_event.type != UnitEventEnum.HTTT:
            app_exception(ErrorCode.INVALID_UNIT_EVENT_TYPE_VALUE)

        submissions = await self.repo.get_all_by_unit_event_id(parsed_unit_event_id)
        unit_ids = list(dict.fromkeys([submission.unitId for submission in submissions]))
        units = await self.unit_repo.list_by_ids(unit_ids)
        unit_map = {str(unit.id): unit for unit in units}

        result: List[UnitEventSubmissionWithUnitResponse] = []
        for submission in submissions:
            unit = unit_map.get(str(submission.unitId))
            if not unit:
                continue
            result.append(
                UnitEventSubmissionWithUnitResponse(
                    id=submission.id,
                    unitEventId=submission.unitEventId,
                    unit=UnitBase(name=unit.name, logo=unit.logo, type=unit.type),
                    content=submission.content or "",
                    evidenceUrl=submission.evidenceUrl or "",
                    status=submission.status,
                    submittedAt=submission.submittedAt,
                )
            )
        return result

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

    async def update_submission_status(
        self, data: UnitEventSubmissionStatusUpdate
    ) -> UnitEventSubmissionResponse:
        submission_id = self._parse_object_id(
            data.unit_event_submission_id, "unit_event_submission_id"
        )
        submission = await self.repo.get_by_id(submission_id)
        if not submission:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_NOT_FOUND)

        submission.status = data.status
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
        if data.list_MSV is None:
            app_exception(ErrorCode.LIST_USER_ID_IS_REQUIRED)
        unit_event_submission = UnitEventSubmission(
            unitEventId=unit_event_id,
            unitId=unit_id,
            content=data.content,
            evidenceUrl=data.evidenceUrl,
            submittedAt=datetime.now(),
        )
        saved = await self.repo.create(unit_event_submission)

        for student_id in data.list_MSV:
            unit_event_submission_member = UnitEventSubmissionMember(
                unitEventSubmissionId=saved.id,
                studentId=student_id,
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

    async def update_unit_event_submission_member(
        self,
        unit_event_id: PydanticObjectId | str,
        x_unit_id: str,
        data: UnitEventSubmissionMemberUpdate,
    ) -> UnitEventSubmissionMemberResponse:
        parsed_unit_event_id = self._parse_object_id(unit_event_id, "unit_event_id")
        parsed_unit_id = self._parse_object_id(x_unit_id, "x_unit_id")

        submission = await self.repo.get_by_unit_event_id_and_unit_id(
            parsed_unit_event_id, parsed_unit_id
        )
        if not submission:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_NOT_FOUND)

        if submission.status == UnitEventSubmissionStatus.APPROVED:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_ALREADY_APPROVED)

        update_data = data.model_dump(exclude_unset=True)
        list_user_id = update_data.pop("list_user_id", None)
        for field, value in update_data.items():
            setattr(submission, field, value)

        if submission.status == UnitEventSubmissionStatus.REJECTED:
            submission.status = UnitEventSubmissionStatus.PENDING
        submission.submittedAt = datetime.now()
        saved = await self.repo.update(submission)

        if list_user_id is not None:
            if len(list_user_id) == 0:
                app_exception(ErrorCode.LIST_USER_ID_IS_REQUIRED)
            await self.unit_event_submission_members_repo.delete_all_by_unit_event_submission_id(
                saved.id
            )
            for user_id in list_user_id:
                await self.unit_event_submission_members_repo.create(
                    UnitEventSubmissionMember(
                        unitEventSubmissionId=saved.id,
                        userId=user_id,
                        checkIn=False,
                    )
                )

        return await self._build_submission_member_response(saved)