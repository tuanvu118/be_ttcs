from repositories.unit_event_repo import UnitEventRepo
from schemas.unit_event import UnitEventCreate, UnitEventResponse, UnitEventUpdate
from schemas.response import BaseResponse
from models.unit_event import UnitEvent, UnitEventEnum
from models.unit_event_assigned_units import UnitEventAssignedUnits
from datetime import datetime, timezone
from beanie import PydanticObjectId
from typing import List
from exceptions import ErrorCode, app_exception
from repositories.unit_event_assigned_units_repo import UnitEventAssignedUnitsRepo
from repositories.unit_repo import UnitRepo
from schemas.unit import UnitBase

class UnitEventService:
    def __init__(
        self,
        repo: UnitEventRepo,
        unit_event_assigned_units_repo: UnitEventAssignedUnitsRepo | None = None,
        unit_repo: UnitRepo | None = None,
    ) -> None:
        self.repo = repo
        self.unit_event_assigned_units_repo = (
            unit_event_assigned_units_repo or UnitEventAssignedUnitsRepo()
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

    async def _ensure_units_exist(
        self, unit_ids: List[PydanticObjectId | str]
    ) -> List[PydanticObjectId]:
        normalized_ids = [self._parse_object_id(unit_id, "unit_id") for unit_id in unit_ids]
        unique_unit_ids = list(dict.fromkeys(normalized_ids))
        units = await self.unit_repo.list_by_ids(unique_unit_ids)
        if len(units) != len(unique_unit_ids):
            app_exception(
                ErrorCode.UNIT_NOT_FOUND,
                extra_detail="Một hoặc nhiều đơn vị được giao không tồn tại",
            )
        return unique_unit_ids

    async def _build_event_response(self, event: UnitEvent) -> UnitEventResponse:
        assigned_links = await self.unit_event_assigned_units_repo.list_by_event_id(event.id)
        unit_ids = [item.unitId for item in assigned_links]
        units = await self.unit_repo.list_by_ids(unit_ids)
        unit_map = {str(unit.id): unit for unit in units}
        assigned_units = [
            UnitBase(
                name=unit_map[str(unit_id)].name,
                logo=unit_map[str(unit_id)].logo,
                type=unit_map[str(unit_id)].type,
            )
            for unit_id in unit_ids
            if str(unit_id) in unit_map
        ]

        return UnitEventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            point=event.point,
            type=event.type,
            created_at=event.created_at,
            created_by=event.created_by,
            assigned_units=assigned_units,
        )

    async def create_unit_event(
        self, 
        payload: UnitEventCreate,
        current_user: str,
    ) -> UnitEventResponse:
        if payload.point < 0 or payload.point > 10 :
            app_exception(ErrorCode.INVALID_POINT_VALUE)
        if payload.type not in UnitEventEnum:
            app_exception(ErrorCode.INVALID_UNIT_EVENT_TYPE_VALUE)

        unique_unit_ids = await self._ensure_units_exist(payload.assigned_units)
            
        unit_event = UnitEvent(
            title=payload.title,
            description=payload.description,
            point=payload.point,
            type=payload.type,
            created_at=datetime.now(timezone.utc),
            created_by=self._parse_object_id(current_user, "current_user_id"),
        )
        saved = await self.repo.create(unit_event)

        for unit_id in unique_unit_ids:
            await self.unit_event_assigned_units_repo.create(UnitEventAssignedUnits(
                unitEventId=saved.id,
                unitId=unit_id
            ))
        return await self._build_event_response(saved)



    async def get_all_unit_events(self) -> List[UnitEventResponse]:
        events = await self.repo.get_all_active()
        return [await self._build_event_response(event) for event in events]

    async def get_unit_event_by_id(self, event_id: PydanticObjectId | str) -> UnitEventResponse:
        parsed_event_id = self._parse_object_id(event_id, "event_id")
        try:
            event = await self.repo.get_by_id(parsed_event_id)
        except Exception:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        if event is None:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        return await self._build_event_response(event)

    async def update_unit_event(self, event_id: PydanticObjectId | str, data: UnitEventUpdate) -> BaseResponse:
        parsed_event_id = self._parse_object_id(event_id, "event_id")
        try:
            event = await self.repo.get_by_id(parsed_event_id)
        except Exception:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        if event is None:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)

        update_data = data.model_dump(exclude_unset=True)
        assigned_units = update_data.pop("assigned_units", None)

        for field, value in update_data.items():
            setattr(event, field, value)

        await self.repo.update(event)

        if assigned_units is not None:
            validated_unit_ids = await self._ensure_units_exist(assigned_units)
            await self.unit_event_assigned_units_repo.delete_by_event_id(event.id)
            for unit_id in validated_unit_ids:
                await self.unit_event_assigned_units_repo.create(
                    UnitEventAssignedUnits(
                        unitEventId=event.id,
                        unitId=unit_id,
                    )
                )

        return BaseResponse(message="Sự kiện đẩy xuống đơn vị đã được cập nhật thành công")

    async def delete_unit_event(self, event_id: PydanticObjectId | str) -> BaseResponse:
        parsed_event_id = self._parse_object_id(event_id, "event_id")
        try:
            event = await self.repo.get_by_id(parsed_event_id)
        except Exception:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        if event is None:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)

        event.deleted_at = datetime.now(timezone.utc)
        await self.repo.update(event)
        return BaseResponse(message="Sự kiện đẩy xuống đơn vị đã được xóa thành công")