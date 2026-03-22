from models.unit_event import UnitEvent
from typing import List
from beanie import PydanticObjectId
from typing import Optional

class UnitEventRepo:
    async def create(self, unit_event: UnitEvent) -> UnitEvent:
        return await unit_event.insert()
    
    async def get_all_active(self) -> List[UnitEvent]:
        return await UnitEvent.find(UnitEvent.deleted_at == None).to_list()

    async def list_by_unit_id(self, unit_id: PydanticObjectId) -> List[UnitEvent]:
        """Lấy danh sách unit_events có unit_id trong listUnitId."""
        return await UnitEvent.find(
            UnitEvent.deleted_at == None,
            UnitEvent.listUnitId == unit_id,
        ).to_list()

    async def get_all(self) -> List[UnitEvent]:
        return await UnitEvent.find_all().to_list()
    
    async def get_by_id(self, unit_event_id: PydanticObjectId) -> Optional[UnitEvent]:
        return await UnitEvent.find_one(
            UnitEvent.id == unit_event_id, UnitEvent.deleted_at == None
        )

    async def update(self, unit_event: UnitEvent) -> UnitEvent:
        return await unit_event.save()
    
    async def delete(self, unit_event: UnitEvent) -> None:
        await unit_event.delete()

