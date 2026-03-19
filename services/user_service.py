from typing import List

from beanie import PydanticObjectId
from fastapi import UploadFile
from fastapi import HTTPException, status
from passlib.context import CryptContext

from exceptions import ErrorCode, app_exception
from models.roles import RoleCode
from models.users_roles import UserRole
from models.users import User
from repositories.role_repo import RoleRepo
from repositories.semester_repo import SemesterRepo
from repositories.unit_repo import UnitRepo
from repositories.user_repo import UserRepo
from repositories.user_role_repo import UserRoleRepo
from schemas.auth import TokenData
from schemas.users import UserCreate, UserRead, UserResponse, UserUpdate
from services.cloudinary_service import upload_image

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class UserService:
    def __init__(
        self,
        repo: UserRepo,
        role_repo: RoleRepo | None = None,
        user_role_repo: UserRoleRepo | None = None,
        unit_repo: UnitRepo | None = None,
        semester_repo: SemesterRepo | None = None,
    ):
        self.repo = repo
        self.role_repo = role_repo or RoleRepo()
        self.user_role_repo = user_role_repo or UserRoleRepo()
        self.unit_repo = unit_repo or UnitRepo()
        self.semester_repo = semester_repo or SemesterRepo()

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_passwod(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def _ensure_update_permission(
        current_user: TokenData,
        target_user_id: PydanticObjectId,
    ) -> None:
        if current_user.sub == str(target_user_id):
            return

        has_admin_or_manager = any(
            "ADMIN" in unit_role.roles or "MANAGER" in unit_role.roles
            for unit_role in current_user.roles
        )
        if not has_admin_or_manager:
            app_exception(ErrorCode.INSUFFICIENT_PERMISSION)

    async def create_user(
        self,
        payload: UserCreate,
        image: UploadFile | None,
    ) -> UserResponse:
        active_semester = await self.semester_repo.get_active()
        if not active_semester:
            app_exception(ErrorCode.ACTIVE_SEMESTER_NOT_FOUND)

        default_unit = await self.unit_repo.get_by_name("DEFAULT")
        if not default_unit:
            app_exception(
                ErrorCode.UNIT_NOT_FOUND,
                extra_detail="Default unit khong ton tai",
            )

        user_role = await self.role_repo.get_by_code(RoleCode.USER)
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Role USER khong ton tai",
            )

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
        saved_user = await self.repo.create(user)

        await self.user_role_repo.create(
            UserRole(
                user_id=saved_user.id,
                role_id=user_role.id,
                unit_id=default_unit.id,
                semester_id=active_semester.id,
                is_active=True,
            )
        )

        return saved_user

    async def get_user(self, user_id: PydanticObjectId) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            app_exception(ErrorCode.USER_NOT_FOUND)
        return user

    async def update_user(
        self,
        user_id: PydanticObjectId,
        payload: UserUpdate,
        image: UploadFile | None,
        current_user: TokenData,
    ) -> UserRead:
        user = await self.repo.get_by_id(user_id)
        if not user:
            app_exception(ErrorCode.USER_NOT_FOUND)

        self._ensure_update_permission(current_user, user_id)

        update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
        password = update_data.pop("password", None)

        for field, value in update_data.items():
            setattr(user, field, value)

        if password:
            user.password_hash = self.hash_password(password)

        if image:
            avatar_url, _ = upload_image(image)
            user.avatar_url = avatar_url

        saved = await self.repo.save(user)
        return UserRead.model_validate(saved)

    async def list_users(self, skip: int = 0, limit: int = 20):
        return await self.repo.get_list(skip=skip, limit=limit)


    async def get_users_by_msv(self, list_msv: List[str]) -> List[User]:
        users = await self.repo.get_by_student_ids(list_msv)
        return users
    
    async def get_users_by_id(self, list_user_id: List[PydanticObjectId]) -> List[User]:
        users = await self.repo.get_by_ids(list_user_id)
        return users
