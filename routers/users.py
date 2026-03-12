from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from repositories.user_repo import UserRepo
from schemas.auth import TokenData
from schemas.users import UserCreate, UserResponse
from security import require_user
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
    return await service.create_user(payload, avatar)


@router.get("/me")
async def read_current_user(current_user: TokenData = Depends(require_user)):
    return current_user
