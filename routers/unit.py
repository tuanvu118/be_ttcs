from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Form, UploadFile, status

from repositories.unit_repo import UnitRepo
from schemas.auth import TokenData
from schemas.unit_member import UnitMemberCreate, UnitMemberRead
from schemas.unit import UnitCreate, UnitRead, UnitUpdate
from security import require_admin, require_user
from services.unit_service import UnitService


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
    name: str = Form(...),
    type: str = Form(...),
    logo: UploadFile | None = None,
    service: UnitService = Depends(get_unit_service),
) -> UnitRead:
    payload = UnitCreate(name=name, type=type)
    return await service.create_unit(payload, logo)


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
    name: str = Form(...),
    type: str = Form(...),
    logo: UploadFile | None = None,
    service: UnitService = Depends(get_unit_service),
) -> UnitRead:
    payload = UnitUpdate(name=name, type=type)
    return await service.update_unit(unit_id, payload, logo)


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


@router.post(
    "/{unit_id}/members",
    response_model=UnitMemberRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_unit_member(
    unit_id: PydanticObjectId,
    payload: UnitMemberCreate,
    current_user: TokenData = Depends(require_user),
    service: UnitService = Depends(get_unit_service),
) -> UnitMemberRead:
    return await service.add_member(
        unit_id=unit_id,
        payload=payload,
        actor_id=PydanticObjectId(current_user.sub),
        current_user=current_user,
    )


@router.get(
    "/{unit_id}/members",
    response_model=List[UnitMemberRead],
)
async def list_unit_members(
    unit_id: PydanticObjectId,
    semester_id: PydanticObjectId | None = None,
    current_user: TokenData = Depends(require_user),
    service: UnitService = Depends(get_unit_service),
) -> List[UnitMemberRead]:
    return await service.list_members(
        unit_id=unit_id,
        current_user=current_user,
        semester_id=semester_id,
    )


@router.delete(
    "/{unit_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_unit_member(
    unit_id: PydanticObjectId,
    user_id: PydanticObjectId,
    semester_id: PydanticObjectId | None = None,
    current_user: TokenData = Depends(require_user),
    service: UnitService = Depends(get_unit_service),
) -> None:
    await service.remove_member(
        unit_id=unit_id,
        user_id=user_id,
        current_user=current_user,
        semester_id=semester_id,
    )
