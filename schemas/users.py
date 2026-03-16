import re
from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, field_validator


class UserBase(BaseModel):
    full_name: str
    email: str
    student_id: str
    class_name: str
    course_code: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None

    @field_validator("email")
    def validate_email(cls, value: str):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, value):
            raise ValueError("Email khong hop le")
        return value


class UserRead(UserBase):
    id: PydanticObjectId

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    student_id: Optional[str] = None
    class_name: Optional[str] = None
    course_code: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None

    @field_validator("email")
    def validate_email(cls, value: Optional[str]):
        if not value or value.strip() == "":
            return None
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, value):
            raise ValueError("Email khong hop le")
        return value.strip()


class UserResponse(UserBase):
    pass


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if len(value) < 6:
            raise ValueError("Mat khau phai >= 6 ky tu")
        return value

class ListMsv(BaseModel):
    list_msv: List[str]

class ListUserId(BaseModel):
    list_user_id: List[PydanticObjectId]