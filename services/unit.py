from typing import List

from beanie import PydanticObjectId

from exceptions import ErrorCode, app_exception
from models.unit import Unit
from repositories.unit_repo import UnitRepo
from schemas.unit import UnitCreate, UnitRead, UnitUpdate


class UnitService:
    def __init__(self, repo: UnitRepo) -> None:
        self.repo = repo

    async def create_unit(self, payload: UnitCreate) -> UnitRead:
        unit = Unit(
            name=payload.name,
            logo=payload.logo,
            type=payload.type,
        )
        saved = await self.repo.create(unit)
        return UnitRead.model_validate(saved)

    async def get_unit(self, unit_id: PydanticObjectId) -> UnitRead:
        unit = await self.repo.get_by_id(unit_id)
        if not unit:
            app_exception(ErrorCode.UNIT_NOT_FOUND)
        return UnitRead.model_validate(unit)

    async def list_units(self) -> List[UnitRead]:
        items = await self.repo.list_all()
        return [UnitRead.model_validate(unit) for unit in items]

    async def update_unit(
        self, unit_id: PydanticObjectId, payload: UnitUpdate
    ) -> UnitRead:
        unit = await self.repo.get_by_id(unit_id)
        if not unit:
            app_exception(ErrorCode.UNIT_NOT_FOUND)

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(unit, field, value)

        saved = await self.repo.update(unit)
        return UnitRead.model_validate(saved)

    async def delete_unit(self, unit_id: PydanticObjectId) -> None:
        unit = await self.repo.get_by_id(unit_id)
        if not unit:
            app_exception(ErrorCode.UNIT_NOT_FOUND)
        await self.repo.delete(unit)
