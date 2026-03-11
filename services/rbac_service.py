from typing import Dict, List, Set

from beanie import PydanticObjectId
from beanie.operators import In
from fastapi import HTTPException, status

from models.roles import Role, RoleCode
from models.users_roles import UserRole
from repositories.role_repo import RoleRepo
from repositories.user_repo import UserRepo
from repositories.user_role_repo import UserRoleRepo

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

    async def build_unit_role_claims_for_user(
        self, user_id: PydanticObjectId
    ) -> List[Dict]:
        user_roles = await self.user_role_repo.list_active_by_user(user_id)
        if not user_roles:
            return []

        role_ids: Set[PydanticObjectId] = {user_role.role_id for user_role in user_roles}
        roles = await Role.find(In(Role.id, list(role_ids))).to_list()
        role_map: Dict[str, str] = {str(role.id): role.code for role in roles}

        by_unit: Dict[str, Set[str]] = {}
        for user_role in user_roles:
            unit_id = str(user_role.unit_id)
            role_code = role_map.get(str(user_role.role_id))
            if not role_code:
                continue
            by_unit.setdefault(unit_id, set()).add(role_code)

        return [
            {"unit_id": unit_id, "roles": list(role_codes)}
            for unit_id, role_codes in by_unit.items()
        ]

    async def assign_role(
        self,
        actor_id: PydanticObjectId,
        target_user_id: PydanticObjectId,
        role_code: str,
        unit_id: PydanticObjectId,
    ) -> UserRole:
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

        user_role = UserRole(
            user_id=target_user.id,
            role_id=role.id,
            unit_id=unit_id,
            is_active=True,
        )
        return await self.user_role_repo.create(user_role)
