from typing import List

from beanie import PydanticObjectId

from exceptions import ErrorCode, app_exception
from models.report import InternalEvent
from repositories.public_event_repo import PublicEventRepository
from repositories.report_repo import ReportRepository
from repositories.semester_repo import SemesterRepo
from schemas.auth import TokenData
from schemas.public_event import PublicEventSummary
from schemas.report import (
    InternalEventCreate,
    InternalEventRead,
    InternalEventUpdate,
    InternalSummary,
    ReportCreate,
    ReportDetail,
    ReportSummary,
    ReportUpdate,
)


class ReportService:
    @staticmethod
    async def _get_report_or_404(report_id: PydanticObjectId):
        report = await ReportRepository.get_by_id(report_id)
        if not report:
            app_exception(ErrorCode.REPORT_NOT_FOUND)
        return report

    @staticmethod
    async def create_report(
        unit_id: PydanticObjectId,
        data: ReportCreate,
    ) -> ReportSummary:
        existing = await ReportRepository.get_by_unique(
            unit_id=unit_id,
            month=data.month,
            year=data.year,
        )

        if existing:
            app_exception(ErrorCode.REPORT_ALREADY_EXISTS)

        report = await ReportRepository.create(
            {
                "unit_id": unit_id,
                "month": data.month,
                "year": data.year,
                "semester_id" : (await SemesterRepo().get_active()).id,
                "public_events": [],
                "internal_events": [],
            }
        )

        return ReportSummary(
            id=report.id,
            unit_id=report.unit_id,
            month=report.month,
            semester_id=report.semester_id,
            year=report.year,
        )

    @staticmethod
    async def update_report(
        report_id: PydanticObjectId,
        data: ReportUpdate,
    ) -> ReportSummary:
        report = await ReportService._get_report_or_404(report_id)

        update_data = data.model_dump(exclude_unset=True)

        new_month = update_data.get("month", report.month)
        new_year = update_data.get("year", report.year)

        existing = await ReportRepository.get_by_unique(
            unit_id=report.unit_id,
            month=new_month,
            year=new_year,
        )

        if existing and existing.id != report.id:
            app_exception(ErrorCode.REPORT_ALREADY_EXISTS)

        for field, value in update_data.items():
            setattr(report, field, value)

        await ReportRepository.save(report)

        return ReportSummary(
            id=report.id,
            unit_id=report.unit_id,
            semester_id=report.semester_id,
            month=report.month,
            year=report.year,
        )

    @staticmethod
    async def get_reports_by_unit(
        unit_id: PydanticObjectId,
    ) -> List[ReportSummary]:
        reports = await ReportRepository.get_by_unit(unit_id)

        return [
            ReportSummary(
                id=report.id,
                unit_id=report.unit_id,
                month=report.month,
                semester_id=report.semester_id,
                year=report.year,
            )
            for report in reports
        ]

    @staticmethod
    async def get_all_reports() -> List[ReportSummary]:
        reports = await ReportRepository.get_all()

        return [
            ReportSummary(
                id=report.id,
                unit_id=report.unit_id,
                semester_id=report.semester_id,
                month=report.month,
                year=report.year,
            )
            for report in reports
        ]

    @staticmethod
    async def get_report_detail(
        report_id: PydanticObjectId,
        current_user: TokenData,
    ) -> ReportDetail:
        report = await ReportService._get_report_or_404(report_id)

        has_global_role = any(
            "ADMIN" in role.roles or "MANAGER" in role.roles
            for role in current_user.roles
        )
        is_staff_of_unit = any(
            "STAFF" in role.roles and str(role.unit_id) == str(report.unit_id)
            for role in current_user.roles
        )

        if not (has_global_role or is_staff_of_unit):
            app_exception(ErrorCode.INSUFFICIENT_PERMISSION)

        public_events = await PublicEventRepository.get_by_ids(report.public_event_ids)

        return ReportDetail(
            id=report.id,
            unit_id=report.unit_id,
            month=report.month,
            year=report.year,
            public_events=[
                PublicEventSummary(
                    id=public_event.id,
                    title=public_event.title,
                )
                for public_event in public_events
            ],
            internal_events=[
                InternalSummary(
                    id=event.id,
                    title=event.title,
                )
                for event in report.internal_events
            ],
        )

    @staticmethod
    async def add_internal_event(
        report_id: PydanticObjectId,
        data: InternalEventCreate,
    ) -> InternalEventRead:
        report = await ReportService._get_report_or_404(report_id)

        event = InternalEvent(**data.model_dump())
        report.internal_events.append(event)

        await ReportRepository.save(report)

        return InternalEventRead(**event.model_dump())

    @staticmethod
    async def update_internal_event(
        report_id: PydanticObjectId,
        event_id: PydanticObjectId,
        data: InternalEventUpdate,
    ) -> InternalEventRead:
        report = await ReportService._get_report_or_404(report_id)

        event = next(
            (item for item in report.internal_events if str(item.id) == str(event_id)),
            None,
        )

        if not event:
            app_exception(ErrorCode.EVENT_NOT_FOUND)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(event, field, value)

        await ReportRepository.save(report)

        return InternalEventRead(**event.model_dump())

    @staticmethod
    async def delete_internal_event(
        report_id: PydanticObjectId,
        event_id: PydanticObjectId,
    ) -> None:
        report = await ReportService._get_report_or_404(report_id)

        original_len = len(report.internal_events)

        report.internal_events = [
            event for event in report.internal_events if str(event.id) != str(event_id)
        ]

        if len(report.internal_events) == original_len:
            app_exception(ErrorCode.EVENT_NOT_FOUND)

        await ReportRepository.save(report)
