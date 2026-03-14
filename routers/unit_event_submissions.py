from fastapi import APIRouter
from schemas.unit_event_submissions import (
    UnitEventSubmissionResponse,
    UnitEventSubmissionUpdate,
)
from typing import List
from beanie import PydanticObjectId
from schemas.auth import TokenData
from security import require_staff
from fastapi import Depends, Header, status
from schemas.unit_event_submissions import UnitEventSubmissionCreate
from services.unit_event_submissions_service import UnitEventSubmissionsService
from repositories.unit_event_submissions_repo import UnitEventSubmissionsRepo

router = APIRouter(prefix="/unit-event-submissions", tags=["Phản hồi Sự kiện"])

def get_unit_event_submission_service() -> UnitEventSubmissionsService:
    return UnitEventSubmissionsService(UnitEventSubmissionsRepo())

@router.post("/HTTT", response_model=UnitEventSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def Phản_hồi_sự_kiện_Hỗ_trợ_Truyền_Thông(
    data: UnitEventSubmissionCreate,
    current_user: TokenData = Depends(require_staff),
    service: UnitEventSubmissionsService = Depends(get_unit_event_submission_service),
) -> UnitEventSubmissionResponse:
    """
    Phản hồi sự kiện Hỗ trợ Truyền Thông
    """
    return await service.create_unit_event_submission(data, current_user.sub)

@router.get("/HTTT", response_model=UnitEventSubmissionResponse)
async def Lấy_phản_hồi_sự_kiện_Hỗ_trợ_Truyền_Thông_theo_sự_kiện_id(
    unit_event_id: PydanticObjectId,
    x_unit_id: str = Header(..., alias="X-Unit-Id"),
    current_user: TokenData = Depends(require_staff),
    service: UnitEventSubmissionsService = Depends(get_unit_event_submission_service),
) -> UnitEventSubmissionResponse:
    """
    Lấy phản hồi sự kiện Hỗ trợ Truyền Thông theo sự kiện id
    """
    return await service.get_unit_event_submissions_by_unit_event_id(
        unit_event_id, x_unit_id
    )


@router.put("/HTTT", response_model=UnitEventSubmissionResponse)
async def Sửa_phản_hồi_sự_kiện_Hỗ_trợ_Truyền_Thông(
    unit_event_id: PydanticObjectId,
    data: UnitEventSubmissionUpdate,
    x_unit_id: str = Header(..., alias="X-Unit-Id"),
    current_user: TokenData = Depends(require_staff),
    service: UnitEventSubmissionsService = Depends(get_unit_event_submission_service),
) -> UnitEventSubmissionResponse:
    """
    Sửa phản hồi sự kiện Hỗ trợ Truyền Thông theo unit_event_id và X-Unit-Id.

    Các trường có thể cập nhật:
    - content: str
    - evidenceUrl: str

    Quyền: Staff đơn vị
    Chỉ có thể sửa khi ở trạng thái PENDING hoặc REJECTED, sau khi sửa sẽ tự động chuyển sang trạng thái PENDING
    """
    return await service.update_unit_event_submission(unit_event_id, x_unit_id, data)