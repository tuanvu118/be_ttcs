from typing import List

from beanie import PydanticObjectId

from exceptions import ErrorCode, app_exception
from models.semester import Semester
from repositories.semester_repo import SemesterRepo
from schemas.semester import SemesterCreate, SemesterRead, SemesterUpdate


class SemesterService:
    def __init__(self, repo: SemesterRepo) -> None:
        self.repo = repo

    @staticmethod
    def _validate_time(start_date, end_date) -> None:
        if start_date >= end_date:
            app_exception(ErrorCode.INVALID_SEMESTER_TIME)

    async def create_semester(self, payload: SemesterCreate) -> SemesterRead:
        self._validate_time(payload.start_date, payload.end_date)

        if payload.is_active:
            await self.repo.deactivate_active_except()

        semester = Semester(**payload.model_dump())
        saved = await self.repo.create(semester)
        return SemesterRead.model_validate(saved)

    async def list_semesters(self) -> List[SemesterRead]:
        semesters = await self.repo.list_all()
        return [SemesterRead.model_validate(semester) for semester in semesters]

    async def get_current_semester(self) -> SemesterRead:
        semester = await self.repo.get_active()
        if not semester:
            app_exception(ErrorCode.ACTIVE_SEMESTER_NOT_FOUND)
        return SemesterRead.model_validate(semester)

    async def get_semester_by_id(self, semester_id: PydanticObjectId) -> SemesterRead:
        semester = await self.repo.get_by_id(semester_id)
        if not semester:
            app_exception(ErrorCode.SEMESTER_NOT_FOUND)
        return SemesterRead.model_validate(semester)

    async def update_semester(
        self,
        semester_id: PydanticObjectId,
        payload: SemesterUpdate,
    ) -> SemesterRead:
        semester = await self.repo.get_by_id(semester_id)
        if not semester:
            app_exception(ErrorCode.SEMESTER_NOT_FOUND)

        update_data = payload.model_dump(exclude_unset=True)

        new_start_date = update_data.get("start_date", semester.start_date)
        new_end_date = update_data.get("end_date", semester.end_date)
        self._validate_time(new_start_date, new_end_date)

        if update_data.get("is_active") is True:
            await self.repo.deactivate_active_except(semester.id)

        for field, value in update_data.items():
            setattr(semester, field, value)

        saved = await self.repo.save(semester)
        return SemesterRead.model_validate(saved)
