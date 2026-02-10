from typing import Dict, List, Set

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from models.roles import Role, RoleCode
from models.users import User
from models.users_roles import UserRole
from repositories.role_repo import RoleRepo
from repositories.user_repo import UserRepo
from repositories.user_role_repo import UserRoleRepo
from beanie.operators import In

ROLE_ADMIN = RoleCode.ADMIN
ROLE_MANAGER = RoleCode.MANAGER
ROLE_STAFF = RoleCode.STAFF
ROLE_USER = RoleCode.USER


class RBACService:
    def __init__(
        self,
        user_repo: UserRepo,
        role_repo: RoleRepo,
        user_role_repo: UserRoleRepo,
    ) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.user_role_repo = user_role_repo

    async def build_role_claims_for_user(
        self, user_id: PydanticObjectId
    ) -> List[Dict]:
        """
        Gom roles theo từng đơn vị để đưa vào JWT.

        Output:
        [
            {"don_vi_id": "<id>", "roles": ["ADMIN", "MANAGER"]},
            ...
        ]
        """
        user_roles = await self.user_role_repo.list_active_by_user(user_id)
        if not user_roles:
            return []

        role_ids: Set[PydanticObjectId] = {ur.role_id for ur in user_roles}
        roles = await Role.find(In(Role.id, list(role_ids))).to_list()
        role_map: Dict[str, str] = {str(r.id): r.code for r in roles}

        by_donvi: Dict[str, Set[str]] = {}
        for ur in user_roles:
            dv_id = str(ur.don_vi_id)
            code = role_map.get(str(ur.role_id))
            if not code:
                continue
            by_donvi.setdefault(dv_id, set()).add(code)

        return [
            {"don_vi_id": dv_id, "roles": list(role_codes)}
            for dv_id, role_codes in by_donvi.items()
        ]

    async def assign_role(
        self,
        actor_id: PydanticObjectId,
        target_user_id: PydanticObjectId,
        role_code: str,
        don_vi_id: PydanticObjectId,
    ) -> UserRole:
        """
        Nghiệp vụ gán role:
        - ADMIN: gán mọi role trên mọi đơn vị.
        - MANAGER: chỉ gán STAFF, USER trong đơn vị mình.
        - STAFF, USER: không được gán role.
        """
        actor = await self.user_repo.get_by_id(actor_id)
        target_user = await self.user_repo.get_by_id(target_user_id)
        if not actor or not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        role = await self.role_repo.get_by_code(role_code)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )

        # TODO: lấy roles của actor theo don_vi_id từ UserRoleRepo nếu cần
        # Ở đây ta chỉ minh hoạ, phần check chi tiết có thể dùng thêm TokenData.

        user_role = UserRole(
            user_id=target_user.id,
            role_id=role.id,
            don_vi_id=don_vi_id,
            is_active=True,
        )
        return await self.user_role_repo.create(user_role)

