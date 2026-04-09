from fastapi import UploadFile
from typing import List, Optional
from repositories.unit_event_repo import UnitEventRepo
from schemas.unit_event import UnitEventCreate, UnitEventResponse, UnitEventUpdate, UnitEventResponseByUnitId
from schemas.response import BaseResponse
from models.unit_event import UnitEvent, UnitEventEnum
from datetime import datetime, timezone
from beanie import PydanticObjectId
from exceptions import ErrorCode, app_exception
from repositories.semester_repo import SemesterRepo
from repositories.unit_repo import UnitRepo
from repositories.user_role_repo import UserRoleRepo
from services.semester_service import SemesterService
from schemas.unit import UnitBase, UnitRead

class UnitEventService:
    def __init__(
        self,
        repo: UnitEventRepo,
        unit_repo: UnitRepo | None = None,
        user_role_repo: UserRoleRepo | None = None,
    ) -> None:
        self.repo = repo
        self.unit_repo = unit_repo or UnitRepo()
        self.user_role_repo = user_role_repo or UserRoleRepo()
        self.semester_service = SemesterService(SemesterRepo())

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
        unit_ids = event.listUnitId or []
        units = await self.unit_repo.list_by_ids(unit_ids)
        unit_map = {str(unit.id): unit for unit in units}
        assigned_units = [
            UnitRead(
                id=unit_map[str(unit_id)].id,
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
            semesterId=event.semesterId,
            created_at=event.created_at,
            created_by=event.created_by,
            assigned_units=assigned_units,
        )

    async def _build_event_response_by_unit_id(self, event: UnitEvent) -> UnitEventResponseByUnitId:
        return UnitEventResponseByUnitId(
            id=event.id,
            title=event.title,
            description=event.description,
            point=event.point,
            type=event.type,
            semesterId=event.semesterId,
            created_at=event.created_at,
        )

    async def create_unit_event(
        self,
        payload: UnitEventCreate,
        current_user: str,
        image: Optional[UploadFile] = None,
    ) -> UnitEventResponse:
        if payload.point < 0 or payload.point > 10:
            app_exception(ErrorCode.INVALID_POINT_VALUE)
        if payload.type not in UnitEventEnum:
            app_exception(ErrorCode.INVALID_UNIT_EVENT_TYPE_VALUE)

        unique_unit_ids = await self._ensure_units_exist(payload.listUnitId)

        image_url = None
        if image:
            from services.cloudinary_service import upload_image
            image_url, _ = upload_image(image)

        unit_event = UnitEvent(
            title=payload.title,
            description=payload.description,
            point=payload.point,
            type=payload.type,
            image_url=image_url,
            semesterId=payload.semesterId or (await self.semester_service.get_current_semester()).id,
            listUnitId=unique_unit_ids,
            created_at=datetime.now(timezone.utc),
            created_by=self._parse_object_id(current_user, "current_user_id"),
        )
        saved = await self.repo.create(unit_event)
        return await self._build_event_response(saved)

    async def get_all_unit_events_by_semester_id(
        self, semester_id: Optional[PydanticObjectId | str] = None
    ) -> List[UnitEventResponse]:
        if semester_id is None or semester_id == 'all':
            events = await self.repo.get_all_active()
            return [await self._build_event_response(event) for event in events]

        parsed_semester_id = self._parse_object_id(semester_id, "semesterId")
        await self.semester_service.get_semester_by_id(parsed_semester_id)
        events = await self.repo.list_active_by_semester_id(parsed_semester_id)
        return [await self._build_event_response(event) for event in events]

    async def get_unit_events_by_unit_id(
        self,
        user_id: PydanticObjectId | str,
        semester_id: PydanticObjectId | str,
    ) -> List[UnitEventResponseByUnitId]:
        parsed_user_id = self._parse_object_id(user_id, "user_id")
        parsed_semester_id = self._parse_object_id(semester_id, "semesterId")
        await self.semester_service.get_semester_by_id(parsed_semester_id)
        
        user_roles = await self.user_role_repo.list_active_by_user(parsed_user_id)
        if not user_roles:
            app_exception(
                ErrorCode.UNIT_NOT_FOUND,
                extra_detail="User chưa được gán vào đơn vị nào",
            )

        unit_ids = list(dict.fromkeys([ur.unit_id for ur in user_roles]))
        seen_event_ids: set[PydanticObjectId] = set()
        events: List[UnitEvent] = []
        for unit_id in unit_ids:
            unit_events = await self.repo.list_by_unit_id_and_semester_id(
                unit_id, parsed_semester_id
            )
            for event in unit_events:
                if event.id not in seen_event_ids:
                    seen_event_ids.add(event.id)
                    events.append(event)

        return [await self._build_event_response_by_unit_id(event) for event in events]

    async def get_unit_event_by_id(self, event_id: PydanticObjectId | str) -> UnitEventResponse:
        parsed_event_id = self._parse_object_id(event_id, "event_id")
        try:
            event = await self.repo.get_by_id(parsed_event_id)
        except Exception:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        if event is None:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        return await self._build_event_response(event)

    async def update_unit_event(
        self, 
        event_id: PydanticObjectId | str, 
        data: UnitEventUpdate,
        image: Optional[UploadFile] = None
    ) -> BaseResponse:
        parsed_event_id = self._parse_object_id(event_id, "event_id")
        try:
            event = await self.repo.get_by_id(parsed_event_id)
        except Exception:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)
        if event is None:
            app_exception(ErrorCode.UNIT_EVENT_NOT_FOUND)

        update_data = data.model_dump(exclude_unset=True)
        
        if image:
            from services.cloudinary_service import upload_image
            image_url, _ = upload_image(image)
            update_data["image_url"] = image_url

        list_unit_id = update_data.pop("listUnitId", None)

        for field, value in update_data.items():
            setattr(event, field, value)

        if list_unit_id is not None:
            validated_unit_ids = await self._ensure_units_exist(list_unit_id)
            event.listUnitId = validated_unit_ids

        await self.repo.update(event)

        return BaseResponse(message="Sự kiện đẩy xuống đơn vị đã được cập nhật thành công")

    async def delete_unit_event(
        self, event_id: PydanticObjectId | str
    ) -> BaseResponse:
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
