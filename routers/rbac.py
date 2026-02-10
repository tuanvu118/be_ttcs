from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from repositories.role_repo import RoleRepo
from repositories.user_repo import UserRepo
from repositories.user_role_repo import UserRoleRepo
from schemas.auth import TokenData
from security import require_admin, require_manager
from services.rbac_service import RBACService


router = APIRouter(prefix="/rbac", tags=["RBAC"])


def get_rbac_service() -> RBACService:
    return RBACService(UserRepo(), RoleRepo(), UserRoleRepo())


@router.post("/assign-role", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role(
    target_user_id: PydanticObjectId,
    role_code: str,
    don_vi_id: PydanticObjectId,
    current_user: TokenData = Depends(require_admin),
    rbac_service: RBACService = Depends(get_rbac_service),
):
    """
    Ví dụ đơn giản: chỉ ADMIN mới được gán role cho user.
    Nếu muốn cho MANAGER gán STAFF/USER, có thể thêm endpoint khác
    với Depends(require_manager) và logic trong RBACService.
    """
    await rbac_service.assign_role(
        actor_id=PydanticObjectId(current_user.sub),
        target_user_id=target_user_id,
        role_code=role_code,
        don_vi_id=don_vi_id,
    )

