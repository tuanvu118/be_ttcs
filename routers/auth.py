from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from exceptions import ErrorCode, app_exception
from repositories.user_repo import UserRepo
from repositories.role_repo import RoleRepo
from repositories.user_role_repo import UserRoleRepo
from schemas.auth import Token
from security import create_access_token
from services.rbac_service import RBACService
from services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_user_service() -> UserService:
    return UserService(UserRepo())


def get_rbac_service() -> RBACService:
    return RBACService(UserRepo(), RoleRepo(), UserRoleRepo())


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
    rbac_service: RBACService = Depends(get_rbac_service),
):
    """
    - form-data: username (ma_sv), password
    (trong Swagger, ô 'username' chính là 'ma_sv')
    Trả về JWT access token chứa roles theo từng đơn vị.
    """
    repo = user_service.repo
    # Ở đây username chính là ma_sv
    user = await repo.get_by_ma_sv(form_data.username)
    if not user or not user_service.verify_passwod(
        form_data.password, user.password_hash
    ):
        app_exception(ErrorCode.INVALID_CREDENTIALS)

    roles_list: List[dict] = await rbac_service.build_role_claims_for_user(user.id)

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "ma_sv": user.ma_sv,
            "is_active": True,
            "roles": roles_list,
        },
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token)

