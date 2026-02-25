from typing import Optional, List, Tuple
from datetime import datetime
from models.users import User
from beanie import PydanticObjectId

class UserRepo:
    async def get_by_id(self,user_id: PydanticObjectId) -> Optional[User]:
        return await User.get(user_id)
    
    async def get_by_email(self,email: str) -> Optional[User]:
        return await User.find_one(User.email == email)

    async def get_by_ma_sv(self,ma_sv: str) -> Optional[User]:
        return await User.find_one(User.ma_sv == ma_sv)

    async def get_list(self, skip: int = 0, limit: int = 20) -> Tuple[List[User], int]:
        total = await User.find().count()
        items = await (
            User.find()
            .sort([("_id", -1)])   # sort theo id, mới nhất trước
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return items, total
    
    async def create(self, user: User) -> User:
        return await user.insert()
    
    async def save(self, user: User) -> User:
        return await user.save()

    @staticmethod
    async def get_by_ids(
            ids: List[PydanticObjectId]
    ) -> List[User]:
        if not ids:
            return []

        return await User.find(
            {"_id": {"$in": ids}}
        ).to_list()
    
    

