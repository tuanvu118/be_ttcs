from datetime import datetime
from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from repositories.user_repo import UserRepo
from schemas.auth import TokenData
from schemas.users import ListMsv, ListUserId, UserCreate, UserRead, UserResponse, UserUpdate
from security import require_staff, require_user
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service() -> UserService:
    return UserService(UserRepo())


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    student_id: str = Form(...),
    class_name: str = Form(...),
    course_code: str = Form(...),
    avatar: UploadFile | None = File(None),
    date_of_birth: datetime = Form(None),
    service: UserService = Depends(get_user_service),
):
    try:
        payload = UserCreate(
            full_name=full_name,
            email=email,
            password=password,
            student_id=student_id,
            class_name=class_name,
            course_code=course_code,
            avatar_url=None,
            date_of_birth=date_of_birth,
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc

    return await service.create_user(payload, avatar)


@router.put("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: PydanticObjectId,
    full_name: str | None = Form(None),
    email: str | None = Form(None),
    password: str | None = Form(None),
    student_id: str | None = Form(None),
    class_name: str | None = Form(None),
    course_code: str | None = Form(None),
    avatar: UploadFile | None = File(None),
    date_of_birth: datetime | None = Form(None),
    current_user: TokenData = Depends(require_user),
    service: UserService = Depends(get_user_service),
) -> UserRead:
    try:
        payload = UserUpdate(
            full_name=full_name,
            email=email,
            password=password,
            student_id=student_id,
            class_name=class_name,
            course_code=course_code,
            date_of_birth=date_of_birth,
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc

    return await service.update_user(user_id, payload, avatar, current_user)


@router.get("/me")
async def read_current_user(current_user: TokenData = Depends(require_user)):
    return current_user


@router.post("/list-users-by-msv")
async def get_users_by_msv(
    data: ListMsv,
    current_user: TokenData = Depends(require_staff),
    service: UserService = Depends(get_user_service),
) -> List[UserRead]:
    return await service.get_users_by_msv(data.list_msv)

@router.post("/list-users-by-id")
async def get_users_by_id(
    data: ListUserId,
    current_user: TokenData = Depends(require_staff),
    service: UserService = Depends(get_user_service),
) -> List[UserRead]:
    return await service.get_users_by_id(data.list_user_id)
