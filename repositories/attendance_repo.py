from beanie import PydanticObjectId

from models.attendance import Attendance


class AttendanceRepository:
    @staticmethod
    async def create(attendance: Attendance) -> Attendance:
        return await attendance.insert()

    @staticmethod
    async def get_by_event_and_user(
        event_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> Attendance | None:
        return await Attendance.find_one(
            Attendance.event_id == event_id,
            Attendance.user_id == user_id,
        )

    @staticmethod
    async def exists_by_event_and_user(
        event_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> bool:
        return await Attendance.find(
            Attendance.event_id == event_id,
            Attendance.user_id == user_id,
        ).count() > 0

    @staticmethod
    async def list_by_event(event_id: PydanticObjectId) -> list[Attendance]:
        return await Attendance.find(
            Attendance.event_id == event_id
        ).sort("-processed_at").to_list()
