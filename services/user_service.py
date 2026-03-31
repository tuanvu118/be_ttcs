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
from repositories.user_unit_repo import UserUnitRepo
from schemas.auth import TokenData
from schemas.users import (
    UserCreate,
    UserListResponse,
    UserProfileResponse,
    UserRead,
    UserResponse,
    UserUpdate,
)
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
        user_unit_repo: UserUnitRepo | None = None,
    ):
        self.repo = repo
        self.role_repo = role_repo or RoleRepo()
        self.user_role_repo = user_role_repo or UserRoleRepo()
        self.unit_repo = unit_repo or UnitRepo()
        self.semester_repo = semester_repo or SemesterRepo()
        self.user_unit_repo = user_unit_repo or UserUnitRepo()

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_passwod(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def _has_admin_or_manager_role(current_user: TokenData) -> bool:
        return any(
            "ADMIN" in unit_role.roles or "MANAGER" in unit_role.roles
            for unit_role in current_user.roles
        )

    @staticmethod
    def _get_staff_unit_ids(current_user: TokenData) -> set[PydanticObjectId]:
        return {
            PydanticObjectId(unit_role.unit_id)
            for unit_role in current_user.roles
            if "STAFF" in unit_role.roles
        }

    @staticmethod
    def _ensure_update_permission(
        current_user: TokenData,
        target_user_id: PydanticObjectId,
    ) -> None:
        if current_user.sub == str(target_user_id):
            return

        if not UserService._has_admin_or_manager_role(current_user):
            app_exception(ErrorCode.INSUFFICIENT_PERMISSION)

    async def _ensure_unique_student_id(
        self,
        student_id: str,
        exclude_user_id: PydanticObjectId | None = None,
    ) -> None:
        existing_user = await self.repo.get_by_student_id(student_id)
        if not existing_user:
            return

        if exclude_user_id is not None and existing_user.id == exclude_user_id:
            return

        app_exception(ErrorCode.STUDENT_ID_ALREADY_EXISTS)

    async def _get_active_semester(self):
        active_semester = await self.semester_repo.get_active()
        if not active_semester:
            app_exception(ErrorCode.ACTIVE_SEMESTER_NOT_FOUND)
        return active_semester

    async def _build_role_claims_for_user(
        self,
        user_id: PydanticObjectId,
    ) -> List[dict]:
        active_semester = await self._get_active_semester()
        user_roles = await self.user_role_repo.list_active_by_user(
            user_id,
            active_semester.id,
        )
        if not user_roles:
            return []

        all_roles = await self.role_repo.list_all()
        role_map = {str(role.id): role.code for role in all_roles}

        by_unit: dict[str, set[str]] = {}
        for user_role in user_roles:
            role_code = role_map.get(str(user_role.role_id))
            if not role_code:
                continue
            unit_id = str(user_role.unit_id)
            by_unit.setdefault(unit_id, set()).add(role_code)

        return [
            {"unit_id": unit_id, "roles": sorted(role_codes)}
            for unit_id, role_codes in by_unit.items()
        ]

    async def _get_visible_user_ids_for_staff(
        self,
        current_user: TokenData,
    ) -> set[PydanticObjectId]:
        staff_unit_ids = self._get_staff_unit_ids(current_user)
        if not staff_unit_ids:
            app_exception(ErrorCode.INSUFFICIENT_PERMISSION)

        active_semester = await self._get_active_semester()
        user_ids: set[PydanticObjectId] = set()
        for unit_id in staff_unit_ids:
            memberships = await self.user_unit_repo.list_active_by_unit(
                unit_id,
                active_semester.id,
            )
            user_ids.update(membership.user_id for membership in memberships)
        return user_ids

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

        await self._ensure_unique_student_id(payload.student_id)

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

    async def get_current_user_profile(
        self,
        current_user: TokenData,
    ) -> UserProfileResponse:
        user = await self.get_user(PydanticObjectId(current_user.sub))
        return UserProfileResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            student_id=user.student_id,
            class_name=user.class_name,
            avatar_url=user.avatar_url,
            date_of_birth=user.date_of_birth,
            is_active=current_user.is_active,
            roles=current_user.roles,
        )

    async def get_user_detail(
        self,
        user_id: PydanticObjectId,
        current_user: TokenData,
    ) -> UserProfileResponse:
        user = await self.get_user(user_id)

        if not self._has_admin_or_manager_role(current_user):
            visible_user_ids = await self._get_visible_user_ids_for_staff(current_user)
            if user.id not in visible_user_ids:
                app_exception(ErrorCode.INSUFFICIENT_PERMISSION)

        return UserProfileResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            student_id=user.student_id,
            class_name=user.class_name,
            avatar_url=user.avatar_url,
            date_of_birth=user.date_of_birth,
            is_active=user.delete_at is None,
            roles=await self._build_role_claims_for_user(user.id),
        )

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

        student_id = update_data.get("student_id")
        if student_id is not None:
            await self._ensure_unique_student_id(student_id, user_id)

        for field, value in update_data.items():
            setattr(user, field, value)

        if password:
            user.password_hash = self.hash_password(password)

        if image:
            avatar_url, _ = upload_image(image)
            user.avatar_url = avatar_url

        saved = await self.repo.save(user)
        return UserRead.model_validate(saved)

    async def update_current_user(
        self,
        payload: UserUpdate,
        image: UploadFile | None,
        current_user: TokenData,
    ) -> UserRead:
        return await self.update_user(
            PydanticObjectId(current_user.sub),
            payload,
            image,
            current_user,
        )

    @staticmethod
    def _sort_users(users: List[User]) -> List[User]:
        return sorted(
            users,
            key=lambda user: (
                user.full_name.lower(),
                user.student_id.lower(),
                user.email.lower(),
            ),
        )

    @staticmethod
    def _matches_text_filter(value: str | None, query: str | None) -> bool:
        if not query:
            return True
        return query.lower() in (value or "").lower()

    @staticmethod
    def _paginate(items: List, skip: int, limit: int) -> List:
        return items[skip : skip + limit]

    async def list_visible_users(
        self,
        current_user: TokenData,
        skip: int = 0,
        limit: int = 20,
        full_name: str | None = None,
        email: str | None = None,
        student_id: str | None = None,
        class_name: str | None = None,
    ) -> UserListResponse:
        if self._has_admin_or_manager_role(current_user):
            users = await self.repo.list_all()
            visible_users = self._sort_users(users)
        else:
            user_ids = await self._get_visible_user_ids_for_staff(current_user)
            if not user_ids:
                return UserListResponse(items=[], total=0, skip=skip, limit=limit)

            users = await self.repo.get_by_ids(list(user_ids))
            visible_users = self._sort_users(users)

        filtered_users = [
            user
            for user in visible_users
            if self._matches_text_filter(user.full_name, full_name)
            and self._matches_text_filter(user.email, email)
            and self._matches_text_filter(user.student_id, student_id)
            and self._matches_text_filter(user.class_name, class_name)
        ]

        total = len(filtered_users)
        paginated_users = self._paginate(filtered_users, skip, limit)
        return UserListResponse(
            items=[UserRead.model_validate(user) for user in paginated_users],
            total=total,
            skip=skip,
            limit=limit,
        )
