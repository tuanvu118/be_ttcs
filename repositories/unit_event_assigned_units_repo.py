from models.unit_event_assigned_units import UnitEventAssignedUnits
from beanie import PydanticObjectId
from typing import Optional, List

class UnitEventAssignedUnitsRepo:
    async def create(self, unit_event_assigned_units: UnitEventAssignedUnits) -> UnitEventAssignedUnits:
        return await unit_event_assigned_units.insert()
    
    async def get_by_id(self, unit_event_assigned_units_id: PydanticObjectId) -> Optional[UnitEventAssignedUnits]:
        return await UnitEventAssignedUnits.get(unit_event_assigned_units_id)
    
    async def get_all(self) -> List[UnitEventAssignedUnits]:
        return await UnitEventAssignedUnits.find_all().to_list()

    async def list_by_event_id(
        self, unit_event_id: PydanticObjectId
    ) -> List[UnitEventAssignedUnits]:
        return await UnitEventAssignedUnits.find(
            UnitEventAssignedUnits.unitEventId == unit_event_id
        ).to_list()
    
    async def update(self, unit_event_assigned_units: UnitEventAssignedUnits) -> UnitEventAssignedUnits:
        return await unit_event_assigned_units.save()

    async def delete_by_event_id(self, unit_event_id: PydanticObjectId) -> None:
        assigned_units = await UnitEventAssignedUnits.find(
            UnitEventAssignedUnits.unitEventId == unit_event_id
        ).to_list()
        for assigned_unit in assigned_units:
            await assigned_unit.delete()