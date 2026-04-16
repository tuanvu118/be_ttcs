from typing import List, Optional
from beanie import PydanticObjectId

from models.report import Report
from models.public_event import PublicEvent


class ReportRepository:

    @staticmethod
    async def create(data: dict) -> Report:
        report = Report(**data)
        await report.insert()
        return report

    @staticmethod
    async def get_by_id(report_id: PydanticObjectId) -> Optional[Report]:
        return await Report.get(report_id)

    @staticmethod
    async def get_by_unique(
        unit_id: PydanticObjectId,
        month: int,
        year: int
    ) -> Optional[Report]:
        return await Report.find_one({
            "unit_id": unit_id,
            "month": month,
            "year": year,
        })

    @staticmethod
    async def get_all() -> List[Report]:
        return await Report.find_all().to_list()

    @staticmethod
    async def get_by_unit(unit_id: PydanticObjectId) -> List[Report]:
        return await Report.find({
            "unit_id": unit_id
        }).to_list()

    @staticmethod
    async def save(report: Report) -> Report:
        await report.save()
        return report

    @staticmethod
    async def delete(report: Report):
        await report.delete()

    @staticmethod
    async def get_filtered(
        month: Optional[int] = None,
        year: Optional[int] = None,
        unit_id: Optional[PydanticObjectId] = None,
        status: Optional[str] = None
    ) -> List[Report]:
        query = {}
        if month is not None:
            query["month"] = month
        if year is not None:
            query["year"] = year
        if unit_id is not None:
            query["unit_id"] = unit_id
        if status is not None:
            query["status"] = status
        
        return await Report.find(query).sort("-updated_at").to_list()

    @staticmethod
    async def get_by_month_year(
        month: int,
        year: int
    ) -> List[Report]:
        return await ReportRepository.get_filtered(month=month, year=year)

    @staticmethod
    async def get_public_events_by_ids(
        ids: List[PydanticObjectId]
    ) -> List[PublicEvent]:

        if not ids:
            return []

        return await PublicEvent.find(
            {"_id": {"$in": ids}}
        ).to_list()