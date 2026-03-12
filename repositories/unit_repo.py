from typing import List, Optional

from beanie import PydanticObjectId

from models.unit import Unit


class UnitRepo:
    async def create(self, unit: Unit) -> Unit:
        return await unit.insert()

    async def get_by_id(self, unit_id: PydanticObjectId) -> Optional[Unit]:
        return await Unit.get(unit_id)

    async def list_all(self) -> List[Unit]:
        return await Unit.find_all().to_list()

    async def delete(self, unit: Unit) -> None:
        await unit.delete()

    async def update(self, unit: Unit) -> Unit:
        return await unit.save()
