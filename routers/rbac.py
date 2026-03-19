from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from repositories.role_repo import RoleRepo
from repositories.semester_repo import SemesterRepo
from repositories.user_repo import UserRepo
from repositories.user_role_repo import UserRoleRepo
from schemas.auth import TokenData
from security import require_admin
from services.rbac_service import RBACService


router = APIRouter(prefix="/rbac", tags=["RBAC"])


def get_rbac_service() -> RBACService:
    return RBACService(UserRepo(), RoleRepo(), UserRoleRepo(), SemesterRepo())


@router.post("/assign-role", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role(
    target_user_id: PydanticObjectId,
    role_id: PydanticObjectId,
    unit_id: PydanticObjectId,
    semester_id: PydanticObjectId | None = None,
    current_user: TokenData = Depends(require_admin),
    rbac_service: RBACService = Depends(get_rbac_service),
):
    await rbac_service.assign_role(
        actor_id=PydanticObjectId(current_user.sub),
        target_user_id=target_user_id,
        role_id=role_id,
        unit_id=unit_id,
        semester_id=semester_id,
    )
