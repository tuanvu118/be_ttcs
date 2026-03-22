from beanie import Document, PydanticObjectId
from typing import Optional

class UnitEventSubmissionMember(Document):
    unitEventSubmissionId: PydanticObjectId
    studentId: Optional[str] = None  # Mã sinh viên (MSV) - dùng khi create
    userId: Optional[PydanticObjectId] = None  # User ID - dùng khi update
    checkIn: bool = False

    class Settings:
        name = "unit_event_submission_members"