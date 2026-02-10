from datetime import datetime
from fastapi import UploadFile
from passlib.context import CryptContext
from beanie import PydanticObjectId
from services.cloudinary_service import upload_image, delete_image

from exceptions import ErrorCode, app_exception
from models.users import User
from repositories.user_repo import UserRepo
from schemas.users import UserCreate, UserResponse, UserRead, UserUpdate

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class UserService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    def hash_password(self, password: str) -> str:
        print("DEBUG password repr:", repr(password))
        print("DEBUG password bytes:", len(password.encode("utf-8")))
        return pwd_context.hash(password)
    
    def verify_passwod(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain,hashed)
    
    async def create_user(self, payload: UserCreate, image: UploadFile) -> UserResponse:
        url = None
        public_id = None
        if image:
            url, public_id = upload_image(image)
        
        user = User(
            ho_ten = payload.ho_ten,
            email=payload.email,
            password_hash=self.hash_password(payload.password),
            ma_sv=payload.ma_sv,
            lop=payload.lop,
            khoa=payload.khoa,
            avatar=url,
            ngay_sinh=payload.ngay_sinh
        )
        return await self.repo.create(user)
    
    async def get_user(self, user_id: PydanticObjectId) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            app_exception(ErrorCode.USER_NOT_FOUND)
        return user

    async def list_users(self, skip: int = 0, limit: int = 20):
        return await self.repo.list(skip=skip, limit=limit)
