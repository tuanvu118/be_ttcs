from typing import Optional
from beanie import Document
from datetime import datetime

class User(Document):
    ho_ten: str
    email: str
    password_hash: str
    ma_sv: str
    lop: str
    khoa: Optional[str] = None
    avatar: Optional[str] = None
    ngay_sinh: Optional[datetime] = None
    delete_at: Optional[datetime] = None

    class Settings:
        name = "users"