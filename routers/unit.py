from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from repositories.unit_repo import UnitRepo
from schemas.auth import TokenData
from schemas.unit import UnitCreate, UnitRead, UnitUpdate
from security import require_admin, require_user
from services.unit import UnitService


router = APIRouter(prefix="/units", tags=["Units"])


def get_unit_service() -> UnitService:
    return UnitService(UnitRepo())


@router.post(
    "",
    response_model=UnitRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_unit(
    payload: UnitCreate,
    service: UnitService = Depends(get_unit_service),
) -> UnitRead:
    return await service.create_unit(payload)


@router.get(
    "",
    response_model=List[UnitRead],
)
async def list_units(
    current_user: TokenData = Depends(require_user),
    service: UnitService = Depends(get_unit_service),
) -> List[UnitRead]:
    return await service.list_units()


@router.get(
    "/{unit_id}",
    response_model=UnitRead,
)
async def get_unit(
    unit_id: PydanticObjectId,
    current_user: TokenData = Depends(require_user),
    service: UnitService = Depends(get_unit_service),
) -> UnitRead:
    return await service.get_unit(unit_id)


@router.put(
    "/{unit_id}",
    response_model=UnitRead,
    dependencies=[Depends(require_admin)],
)
async def update_unit(
    unit_id: PydanticObjectId,
    payload: UnitUpdate,
    service: UnitService = Depends(get_unit_service),
) -> UnitRead:
    return await service.update_unit(unit_id, payload)


@router.delete(
    "/{unit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_unit(
    unit_id: PydanticObjectId,
    service: UnitService = Depends(get_unit_service),
) -> None:
    await service.delete_unit(unit_id)
