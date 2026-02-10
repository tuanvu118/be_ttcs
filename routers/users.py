from datetime import datetime
from typing import Annotated

from beanie import PydanticObjectId
from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
    UploadFile,
    HTTPException,
    Form,
    File,
)

from repositories.user_repo import UserRepo
from schemas.response import BaseResponse
from schemas.users import UserCreate, UserResponse
from schemas.auth import TokenData
from security import require_user
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service() -> UserService:
    return UserService(UserRepo())


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    ho_ten: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    ma_sv: str = Form(...),
    lop: str = Form(...),
    khoa: str = Form(...),
    avatar: UploadFile | None = File(None),
    ngay_sinh: datetime = Form(None),
    service: UserService = Depends(get_user_service),
):
    payload = UserCreate(
        ho_ten=ho_ten,
        email=email,
        password=password,
        ma_sv=ma_sv,
        lop=lop,
        khoa=khoa,
        avatar=None,
        ngay_sinh=ngay_sinh,
    )
    return await service.create_user(payload, avatar)


@router.get("/me")
async def read_current_user(current_user: TokenData = Depends(require_user)):
    """
    Endpoint cá nhân: chỉ xem dữ liệu user đang đăng nhập.
    """
    return current_user
