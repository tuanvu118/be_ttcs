from models.unit_event import UnitEvent
from typing import List
from beanie import PydanticObjectId
from typing import Optional

class UnitEventRepo:
    async def create(self, unit_event: UnitEvent) -> UnitEvent:
        return await unit_event.insert()
    
    async def get_all(self) -> List[UnitEvent]:
        return await UnitEvent.find_all().to_list()
    
    async def get_by_id(self, unit_event_id: PydanticObjectId) -> Optional[UnitEvent]:
        return await UnitEvent.get(unit_event_id)

    async def update(self, unit_event: UnitEvent) -> UnitEvent:
        return await unit_event.save()
    
    async def delete(self, unit_event: UnitEvent) -> None:
        await unit_event.delete()

