from fastapi import APIRouter, Depends
from fastapi import status
from schemas.unit_event import UnitEventCreate, UnitEventResponse
from security import require_manager
from services.unit_event_service import UnitEventService
from repositories.unit_event_repo import UnitEventRepo
from schemas.auth import TokenData

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
    Create a new unit event
    """
    return await service.create_unit_event(data, current_user.sub)