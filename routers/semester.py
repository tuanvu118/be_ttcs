from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from repositories.semester_repo import SemesterRepo
from schemas.auth import TokenData
from schemas.semester import SemesterCreate, SemesterRead, SemesterUpdate
from security import require_global_admin, require_user
from services.semester_service import SemesterService


router = APIRouter(prefix="/semesters", tags=["Semesters"])


def get_semester_service() -> SemesterService:
    return SemesterService(SemesterRepo())


@router.post(
    "",
    response_model=SemesterRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_semester(
    payload: SemesterCreate,
    current_user: TokenData = Depends(require_global_admin),
    service: SemesterService = Depends(get_semester_service),
) -> SemesterRead:
    return await service.create_semester(payload)


@router.get(
    "",
    response_model=List[SemesterRead],
)
async def list_semesters(
    current_user: TokenData = Depends(require_user),
    service: SemesterService = Depends(get_semester_service),
) -> List[SemesterRead]:
    return await service.list_semesters()


@router.get(
    "/current",
    response_model=SemesterRead,
)
async def get_current_semester(
    current_user: TokenData = Depends(require_user),
    service: SemesterService = Depends(get_semester_service),
) -> SemesterRead:
    return await service.get_current_semester()


@router.put(
    "/{semester_id}",
    response_model=SemesterRead,
)
async def update_semester(
    semester_id: PydanticObjectId,
    payload: SemesterUpdate,
    current_user: TokenData = Depends(require_global_admin),
    service: SemesterService = Depends(get_semester_service),
) -> SemesterRead:
    return await service.update_semester(semester_id, payload)
