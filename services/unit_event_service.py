from beanie.odm.actions import P
from repositories.unit_event_repo import UnitEventRepo
from schemas.unit_event import UnitEventCreate, UnitEventResponse
from models.unit_event import UnitEvent, UnitEventEnum
from datetime import datetime, timezone
from beanie import PydanticObjectId
from typing import List
from exceptions import ErrorCode, app_exception

class UnitEventService:
    def __init__(self, repo: UnitEventRepo) -> None:
        self.repo = repo

    async def create_unit_event(
        self, 
        payload: UnitEventCreate,
        current_user: str,
    ) -> UnitEventResponse:
        if payload.point < 0 or payload.point > 10 :
            app_exception(ErrorCode.INVALID_POINT_VALUE)
        if payload.type not in UnitEventEnum:
            app_exception(ErrorCode.INVALID_UNIT_EVENT_TYPE_VALUE)
            
        unit_event = UnitEvent(
            title=payload.title,
            description=payload.description,
            point=payload.point,
            type=payload.type,
            created_at=datetime.now(timezone.utc),
            created_by=PydanticObjectId(current_user)
        )
        saved = await self.repo.create(unit_event)
        return UnitEventResponse.model_validate(saved)



    async def get_all_unit_events(self) -> List[UnitEventResponse]:
        events = await self.repo.get_all()
        return [UnitEventResponse.model_validate(event) for event in events]