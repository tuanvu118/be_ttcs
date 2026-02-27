from fastapi import APIRouter, Depends
from fastapi import status
from schemas.unit_event import UnitEventCreate, UnitEventResponse
from security import require_manager
from services.unit_event_service import UnitEventService
from repositories.unit_event_repo import UnitEventRepo
from schemas.auth import TokenData
from typing import List

router = APIRouter(prefix="/unit-events", tags=["Unit Events"])

def get_unit_event_service() -> UnitEventService:
    return UnitEventService(UnitEventRepo())

@router.post("/", 
response_model=UnitEventResponse,
status_code=status.HTTP_201_CREATED,
dependencies=[Depends(require_manager)]
)

async def tạo_sự_kiện_đẩy_xuống_đơn_vị(
    data: UnitEventCreate,
    current_user: TokenData = Depends(require_manager),
    service: UnitEventService = Depends(get_unit_event_service),
) -> UnitEventResponse:
    """
    Tạo sự kiện đẩy xuống đơn vị (HTTT hoặc HTSK)

    Điểm số từ 0.00 đến 10.00

    Loại sự kiện: HTTT hoặc HTSK

    Quyền tạo: VPĐ hoặc ADMIN
    """
    return await service.create_unit_event(data, current_user.sub)

@router.get("/", response_model=List[UnitEventResponse], dependencies=[Depends(require_manager)])
async def Lấy_danh_sách_tất_cả_sự_kiện_đẩy_xuống_đơn_vị(
    _ = Depends(require_manager),
    service: UnitEventService = Depends(get_unit_event_service),
) -> List[UnitEventResponse]:
    """
    Lấy danh sách tất cả sự kiện đẩy xuống đơn vị (bao gồm cả HTTT và HTSK)
    
    Quyền xem: VPĐ hoặc ADMIN
    """
    return await service.get_all_unit_events()