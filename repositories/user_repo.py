from typing import List, Optional, Tuple

from beanie import PydanticObjectId

from models.users import User


class UserRepo:
    async def get_by_id(self, user_id: PydanticObjectId) -> Optional[User]:
        return await User.get(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await User.find_one(User.email == email)

    async def get_by_student_id(self, student_id: str) -> Optional[User]:
        return await User.find_one(User.student_id == student_id)

    async def get_list(self, skip: int = 0, limit: int = 20) -> Tuple[List[User], int]:
        total = await User.find().count()
        items = await User.find().sort([("_id", -1)]).skip(skip).limit(limit).to_list()
        return items, total

    async def create(self, user: User) -> User:
        return await user.insert()

    async def save(self, user: User) -> User:
        return await user.save()

    @staticmethod
    async def get_by_ids(ids: List[PydanticObjectId]) -> List[User]:
        if not ids:
            return []

        return await User.find({"_id": {"$in": ids}}).to_list()
