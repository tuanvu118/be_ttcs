from typing import List,Optional
from beanie import PydanticObjectId
import re
from pydantic import BaseModel,field_validator,ConfigDict
from models.users import User
from fastapi_pagination import Params
from datetime import datetime

class UserBase(BaseModel):
    ho_ten: str
    email: str
    ma_sv: str
    lop: str
    khoa: Optional[str] = None
    avatar: Optional[str] = None
    ngay_sinh: Optional[datetime] = None

    @field_validator("email")
    def validate_email(cls, v):
        if v is None:
            return None
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, v):
            raise ValueError("Email không hợp lệ")
        return v    
    
class UserRead(UserBase):
    id: PydanticObjectId
    model_config = ConfigDict(from_attributes=True)    

class UserUpdate(BaseModel):
    ho_ten: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    ma_sv: Optional[str] = None
    lop: Optional[str] = None
    khoa: Optional[str] = None
    ngay_sinh: Optional[datetime] = None
    
    @field_validator("email")
    def validate_email(cls, v):
        if not v or v.strip() == "":
            return None  # Không cập nhật nếu chuỗi rỗng
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, v):
            return ValueError("Email không hợp lệ")
        return v.strip()
    
class UserResponse(UserBase):
    pass

class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if len(v) < 6:
            raise ValueError("Mật khẩu phải >= 6 ký tự")
        return v