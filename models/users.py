from datetime import datetime
from typing import Optional

from beanie import Document


class User(Document):
    full_name: str
    email: str
    password_hash: str
    student_id: str
    class_name: str
    course_code: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    delete_at: Optional[datetime] = None

    class Settings:
        name = "users"
