from repositories.unit_event_submissions_repo import UnitEventSubmissionsRepo
from repositories.unit_event_submission_members_repo import UnitEventSubmissionMembersRepo
from repositories.unit_repo import UnitRepo
from repositories.user_repo import UserRepo
from repositories.user_unit_repo import UserUnitRepo
from schemas.unit_event_submissions import (
    UnitEventSubmissionCreate,
    UnitEventSubmissionResponse,
    UnitEventSubmissionUpdate,
    UnitEventSubmissionStatusUpdate,
    UnitEventSubmissionMemberCreate,
    UnitEventSubmissionMemberUpdate,
    UnitEventSubmissionMemberResponse,
    UnitEventSubmissionWithUnitResponse,
    UnitEventSubmissionHTSKListItemResponse,
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
from schemas.users import UserRead

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
        self.user_repo = UserRepo()
        self.user_unit_repo = UserUnitRepo()
    def _parse_object_id(self, value: PydanticObjectId | str, field_name: str) -> PydanticObjectId:
        try:
            return PydanticObjectId(str(value))
        except Exception:
            app_exception(
                ErrorCode.INVALID_ID_FORMAT,
                extra_detail=f"{field_name} không đúng định dạng",
            )

    def _ensure_unit_assigned_to_event(
        self, unit_event: UnitEvent, unit_id: PydanticObjectId
    ) -> dict[str, PydanticObjectId]:
        """Kiểm tra đơn vị có trong listUnitId của sự kiện."""
        list_unit_id = unit_event.listUnitId or []
        if unit_id not in list_unit_id:
            app_exception(ErrorCode.UNIT_NOT_ASSIGNED_TO_EVENT)

    async def _build_submission_member_response(
        self, submission: UnitEventSubmission
    ) -> UnitEventSubmissionMemberResponse:
        members = await self.unit_event_submission_members_repo.get_all_by_unit_event_submission_id(
            submission.id
        )
        list_user_id = []
        for member in members:
            if member.studentId is not None:
                list_user_id.append(member.studentId)
            elif member.userId is not None:
                list_user_id.append(member.userId)
        return UnitEventSubmissionMemberResponse(
            unitEventId=submission.unitEventId,
            unitId=submission.unitId,
            content=submission.content or "",
            evidenceUrl=submission.evidenceUrl or "",
            status=submission.status,
            submittedAt=submission.submittedAt,
            list_user_id=list_user_id,
        )

    async def _validate_students_belong_to_unit(
        self,
        student_ids: List[str],
        unit_id: PydanticObjectId,
        semester_id: PydanticObjectId,
    ) -> dict[str, PydanticObjectId]:
        normalized_student_ids = [str(student_id).strip() for student_id in student_ids if str(student_id).strip()]
        if not normalized_student_ids:
            app_exception(ErrorCode.LIST_USER_ID_IS_REQUIRED)

        users = await self.user_repo.get_by_student_ids(normalized_student_ids)
        user_by_student_id = {user.student_id: user for user in users}
        missing_student_ids = [
            student_id for student_id in normalized_student_ids if student_id not in user_by_student_id
        ]
        if missing_student_ids:
            app_exception(
                ErrorCode.USER_NOT_IN_UNIT,
                extra_detail="Sinh viên không thuộc đơn vị do bạn quản lý",
            )

        user_ids = [user.id for user in users]
        active_memberships = await self.user_unit_repo.list_active_by_unit_and_users(
            unit_id, semester_id, user_ids
        )
        active_user_ids = {membership.user_id for membership in active_memberships}
        invalid_student_ids = [
            student_id
            for student_id in normalized_student_ids
            if user_by_student_id[student_id].id not in active_user_ids
        ]
        if invalid_student_ids:
            app_exception(
                ErrorCode.USER_NOT_IN_UNIT,
                extra_detail="Sinh viên không thuộc đơn vị do bạn quản lý",
            )

        return {
            student_id: user_by_student_id[student_id].id
            for student_id in normalized_student_ids
        }

    async def create_unit_event_submission(self, data: UnitEventSubmissionCreate, current_user: str) -> UnitEventSubmissionResponse:
        unit_event_id = self._parse_object_id(data.unitEventId, "unitEventId")
        unit_event = await UnitEvent.get(unit_event_id)
        if not unit_event:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        if unit_event.type != UnitEventEnum.HTTT:
            app_exception(ErrorCode.INVALID_UNIT_EVENT_TYPE_VALUE)
        unit_id = self._parse_object_id(data.unitId, "unitId")
        self._ensure_unit_assigned_to_event(unit_event, unit_id)
        existing_submission = await self.repo.get_by_unit_event_id_and_unit_id(unit_event_id, unit_id)
        if existing_submission:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_ALREADY_EXISTS)
        unit_event_submission = UnitEventSubmission(
            unitEventId=unit_event_id,
            unitId=unit_id,
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
        unit_event = await UnitEvent.get(parsed_unit_event_id)
        if not unit_event:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        self._ensure_unit_assigned_to_event(unit_event, parsed_unit_id)
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
        unit_event = await UnitEvent.get(parsed_unit_event_id)
        if not unit_event:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        self._ensure_unit_assigned_to_event(unit_event, parsed_unit_id)

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
        self._ensure_unit_assigned_to_event(unit_event, unit_id)
        existing_submission = await self.repo.get_by_unit_event_id_and_unit_id(unit_event_id, unit_id)
        if existing_submission:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_ALREADY_EXISTS)
        if data.list_MSV is None:
            app_exception(ErrorCode.LIST_USER_ID_IS_REQUIRED)
        user_ids_by_student_id = await self._validate_students_belong_to_unit(
            data.list_MSV, unit_id, unit_event.semesterId
        )
        unit_event_submission = UnitEventSubmission(
            unitEventId=unit_event_id,
            unitId=unit_id,
            content=data.content,
            evidenceUrl=getattr(data, "evidenceUrl", None) or "",
            submittedAt=datetime.now(),
        )
        saved = await self.repo.create(unit_event_submission)

        for student_id in data.list_MSV:
            unit_event_submission_member = UnitEventSubmissionMember(
                unitEventSubmissionId=saved.id,
                studentId=student_id,
                userId=user_ids_by_student_id[str(student_id).strip()],
                checkIn=False,
            )
            await self.unit_event_submission_members_repo.create(unit_event_submission_member)

        return await self._build_submission_member_response(saved)


    async def get_unit_event_submissions_HTSK_by_unit_event_id(
        self, unit_event_id: PydanticObjectId | str, x_unit_id: str
    ) -> UnitEventSubmissionMemberResponse:
        parsed_unit_event_id = self._parse_object_id(unit_event_id, "unit_event_id")
        parsed_unit_id = self._parse_object_id(x_unit_id, "x_unit_id")
        unit_event = await UnitEvent.get(parsed_unit_event_id)
        if not unit_event:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        self._ensure_unit_assigned_to_event(unit_event, parsed_unit_id)
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
        unit_event = await UnitEvent.get(parsed_unit_event_id)
        if not unit_event:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        self._ensure_unit_assigned_to_event(unit_event, parsed_unit_id)

        submission = await self.repo.get_by_unit_event_id_and_unit_id(
            parsed_unit_event_id, parsed_unit_id
        )
        if not submission:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_NOT_FOUND)

        if submission.status == UnitEventSubmissionStatus.APPROVED:
            app_exception(ErrorCode.UNIT_EVENT_SUBMISSION_ALREADY_APPROVED)

        update_data = data.model_dump(exclude_unset=True)
        list_MSV = update_data.pop("list_MSV", None)
        if list_MSV is not None:
            list_MSV = [str(x).strip() for x in list_MSV if str(x).strip()]
        for field, value in update_data.items():
            setattr(submission, field, value)

        if submission.status == UnitEventSubmissionStatus.REJECTED:
            submission.status = UnitEventSubmissionStatus.PENDING
        submission.submittedAt = datetime.now()
        saved = await self.repo.update(submission)

        if list_MSV is not None:
            if len(list_MSV) == 0:
                app_exception(ErrorCode.LIST_USER_ID_IS_REQUIRED)
            user_ids_by_student_id = await self._validate_students_belong_to_unit(
                list_MSV, parsed_unit_id, unit_event.semesterId
            )
            await self.unit_event_submission_members_repo.delete_all_by_unit_event_submission_id(
                saved.id
            )
            for student_id in list_MSV:
                await self.unit_event_submission_members_repo.create(
                    UnitEventSubmissionMember(
                        unitEventSubmissionId=saved.id,
                        studentId=student_id,
                        userId=user_ids_by_student_id[str(student_id).strip()],
                        checkIn=False,
                    )
                )

        return await self._build_submission_member_response(saved)

    async def get_all_htsk_members_by_unit_event_id(
        self, unit_event_id: PydanticObjectId | str
    ) -> List[UnitEventSubmissionHTSKListItemResponse]:
        parsed_unit_event_id = self._parse_object_id(unit_event_id, "unit_event_id")
        unit_event = await UnitEvent.get(parsed_unit_event_id)
        if not unit_event:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        if unit_event.type != UnitEventEnum.HTSK:
            app_exception(ErrorCode.INVALID_UNIT_EVENT_TYPE_VALUE)

        submissions = await self.repo.get_all_by_unit_event_id(parsed_unit_event_id)
        if not submissions:
            return []

        submission_ids = [submission.id for submission in submissions]
        members = await self.unit_event_submission_members_repo.get_all_by_unit_event_submission_ids(
            submission_ids
        )
        if not members:
            return []

        unit_ids = list({submission.unitId for submission in submissions})
        units = await self.unit_repo.list_by_ids(unit_ids)
        unit_name_map = {str(unit.id): unit.name for unit in units}

        submission_unit_map = {str(submission.id): submission.unitId for submission in submissions}

        user_id_members = [member.userId for member in members if member.userId is not None]
        student_ids = [
            str(member.studentId).strip()
            for member in members
            if member.userId is None and member.studentId is not None and str(member.studentId).strip()
        ]

        users_by_id = {
            str(user.id): user for user in await UserRepo.get_by_ids(user_id_members)
        }
        users_by_student_id = {
            user.student_id: user for user in await self.user_repo.get_by_student_ids(student_ids)
        }

        result: List[UnitEventSubmissionHTSKListItemResponse] = []
        for member in members:
            user = None
            if member.userId is not None:
                user = users_by_id.get(str(member.userId))
            elif member.studentId is not None:
                user = users_by_student_id.get(str(member.studentId).strip())
            if user is None:
                continue

            unit_id = submission_unit_map.get(str(member.unitEventSubmissionId))
            if unit_id is None:
                continue
            unit_name = unit_name_map.get(str(unit_id), "")

            result.append(
                UnitEventSubmissionHTSKListItemResponse(
                    user=UserRead.model_validate(user),
                    unit_name=unit_name,
                    checkIn=member.checkIn,
                )
            )
        return result
