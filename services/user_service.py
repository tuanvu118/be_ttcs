from fastapi import UploadFile
from beanie import PydanticObjectId
from passlib.context import CryptContext

from exceptions import ErrorCode, app_exception
from models.users import User
from repositories.user_repo import UserRepo
from schemas.users import UserCreate, UserResponse
from services.cloudinary_service import upload_image
from typing import List

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class UserService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_passwod(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    async def create_user(
        self,
        payload: UserCreate,
        image: UploadFile | None,
    ) -> UserResponse:
        avatar_url = None
        if image:
            avatar_url, _ = upload_image(image)

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=self.hash_password(payload.password),
            student_id=payload.student_id,
            class_name=payload.class_name,
            course_code=payload.course_code,
            avatar_url=avatar_url,
            date_of_birth=payload.date_of_birth,
        )
        return await self.repo.create(user)

    async def get_user(self, user_id: PydanticObjectId) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            app_exception(ErrorCode.USER_NOT_FOUND)
        return user

    async def list_users(self, skip: int = 0, limit: int = 20):
        return await self.repo.get_list(skip=skip, limit=limit)


    async def get_users_by_msv(self, list_msv: List[str]) -> List[User]:
        users = await self.repo.get_by_student_ids(list_msv)
        return users
    
    async def get_users_by_id(self, list_user_id: List[PydanticObjectId]) -> List[User]:
        users = await self.repo.get_by_ids(list_user_id)
        return users