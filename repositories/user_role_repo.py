from typing import List

from beanie import PydanticObjectId

from models.users_roles import UserRole


class UserRoleRepo:
    async def list_by_user(self, user_id: PydanticObjectId) -> List[UserRole]:
        return await UserRole.find(
            UserRole.user_id == user_id
        ).to_list()

    async def list_active_by_user(self, user_id: PydanticObjectId) -> List[UserRole]:
        return await UserRole.find(
            UserRole.user_id == user_id,
            UserRole.is_active == True,
        ).to_list()

    async def list_active_by_user_and_don_vi(
        self, user_id: PydanticObjectId, don_vi_id: PydanticObjectId
    ) -> List[UserRole]:
        return await UserRole.find(
            UserRole.user_id == user_id,
            UserRole.don_vi_id == don_vi_id,
            UserRole.is_active == True,
        ).to_list()

    async def create(self, user_role: UserRole) -> UserRole:
        return await user_role.insert()

    async def deactivate(self, user_role: UserRole) -> UserRole:
        user_role.is_active = False
        return await user_role.save()
