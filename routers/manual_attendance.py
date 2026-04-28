from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status

from schemas.attendance import AttendanceRead, ManualAttendanceRequest
from schemas.auth import TokenData
from security import require_admin_or_manager_global
from services.manual_attendance_service import ManualAttendanceService

router = APIRouter(prefix="/manual-attendance", tags=["Manual Attendance"])

@router.post(
    "/mark",
    response_model=AttendanceRead,
    status_code=status.HTTP_201_CREATED,
)
async def mark_manual_attendance(
    request_body: ManualAttendanceRequest,
    current_user: TokenData = Depends(require_admin_or_manager_global),
):
    """
    Điểm danh thủ công cho sinh viên (chỉ dành cho Admin/Manager).
    """
    return await ManualAttendanceService.mark_manual_attendance(
        actor_id=PydanticObjectId(current_user.sub),
        request=request_body,
    )
