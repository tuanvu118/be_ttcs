from repositories.unit_event_repo import UnitEventRepo
from schemas.unit_event import UnitEventCreate, UnitEventResponse
from models.unit_event import UnitEvent
from datetime import datetime, timezone
from beanie import PydanticObjectId
from security import get_current_user

class UnitEventService:
    def __init__(self, repo: UnitEventRepo) -> None:
        self.repo = repo

    async def create_unit_event(
        self, 
        payload: UnitEventCreate,
        current_user: str,
    ) -> UnitEventResponse:
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