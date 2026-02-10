import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from exceptions import ErrorCode, app_exception
from schemas.auth import DonViRole, TokenData


SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            app_exception(ErrorCode.INVALID_TOKEN)
        roles_payload = payload.get("roles", [])
        roles: List[DonViRole] = [DonViRole(**item) for item in roles_payload]
        token_data = TokenData(
            sub=str(payload.get("sub")),
            email=payload.get("email"),
            is_active=payload.get("is_active", True),
            roles=roles,
        )
    except (JWTError, ValueError, TypeError):
        app_exception(ErrorCode.INVALID_TOKEN)
    return token_data


def _has_role_in_donvi(
    current_user: TokenData,
    required_roles: List[str],
    don_vi_id: str,
) -> bool:
    for dv in current_user.roles:
        if dv.don_vi_id == don_vi_id and any(r in dv.roles for r in required_roles):
            return True
    return False


def require_admin(
    current_user: TokenData = Depends(get_current_user),
    x_don_vi_id: str | None = Header(default=None, alias="X-DonVi-Id"),
) -> TokenData:
    if x_don_vi_id is None:
        app_exception(ErrorCode.HEADER_DONVI_REQUIRED)
    if not _has_role_in_donvi(current_user, ["ADMIN"], x_don_vi_id):
        app_exception(ErrorCode.INSUFFICIENT_PERMISSION, extra_detail="ADMIN role required")
    return current_user


def require_manager(
    current_user: TokenData = Depends(get_current_user),
    x_don_vi_id: str | None = Header(default=None, alias="X-DonVi-Id"),
) -> TokenData:
    if x_don_vi_id is None:
        app_exception(ErrorCode.HEADER_DONVI_REQUIRED)
    if not _has_role_in_donvi(current_user, ["ADMIN", "MANAGER"], x_don_vi_id):
        app_exception(
            ErrorCode.INSUFFICIENT_PERMISSION,
            extra_detail="MANAGER or higher required",
        )
    return current_user


def require_staff(
    current_user: TokenData = Depends(get_current_user),
    x_don_vi_id: str | None = Header(default=None, alias="X-DonVi-Id"),
) -> TokenData:
    if x_don_vi_id is None:
        app_exception(ErrorCode.HEADER_DONVI_REQUIRED)
    if not _has_role_in_donvi(
        current_user, ["ADMIN", "MANAGER", "STAFF"], x_don_vi_id
    ):
        app_exception(
            ErrorCode.INSUFFICIENT_PERMISSION,
            extra_detail="STAFF or higher required",
        )
    return current_user


def require_user(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    # Bất kỳ user đăng nhập hợp lệ đều pass
    return current_user

