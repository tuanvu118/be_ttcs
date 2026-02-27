from models.unit_event import UnitEvent

class UnitEventRepo:
    async def create(self, unit_event: UnitEvent) -> UnitEvent:
        return await unit_event.insert()