from fastapi import APIRouter, Depends, Query
from fastapi import status
from schemas.unit_event import (
    UnitEventCreate,
    UnitEventResponse,
    UnitEventResponseByUnitId,
    UnitEventUpdate,
    UnitEventPaginationResponse,
)
from schemas.response import BaseResponse
from security import require_manager, require_staff
from services.unit_event_service import UnitEventService
from repositories.unit_event_repo import UnitEventRepo
from schemas.auth import TokenData
from typing import List, Optional
from beanie import PydanticObjectId

router = APIRouter(prefix="/unit-events", tags=["Unit Events"])

def get_unit_event_service() -> UnitEventService:
    return UnitEventService(UnitEventRepo())

import json
from fastapi import Form

@router.post("/", 
response_model=UnitEventResponse,
status_code=status.HTTP_201_CREATED,
dependencies=[Depends(require_manager)]
)
async def Create_Unit_Event(
    title: str = Form(...),
    description: str = Form(None),
    point: float = Form(0),
    type: str = Form(...),
    listUnitId: str = Form("[]"),
    semester_id: Optional[str] = Form(None),
    current_user: TokenData = Depends(require_manager),
    service: UnitEventService = Depends(get_unit_event_service),
) -> UnitEventResponse:
    """
    Tạo sự kiện đẩy xuống đơn vị (HTTT hoặc HTSK) với sự hỗ trợ của Multipart/Form-data.
    """
    from schemas.unit_event import UnitEventCreate
    from decimal import Decimal
    
    # Parse listUnitId từ JSON string
    unit_ids = json.loads(listUnitId)
    
    data = UnitEventCreate(
        title=title,
        description=description,
        point=Decimal(str(point)),
        type=type,
        listUnitId=unit_ids,
        semesterId=PydanticObjectId(semester_id) if semester_id else None
    )
    
    return await service.create_unit_event(data, current_user.sub)

@router.get("/all", response_model=UnitEventPaginationResponse, dependencies=[Depends(require_manager)])
async def Get_All_Unit_Events_By_Semester(
    semester_id: Optional[PydanticObjectId] = Query(None, alias="semesterId"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    _ = Depends(require_manager),
    service: UnitEventService = Depends(get_unit_event_service),
) -> UnitEventPaginationResponse:
    """
    Lấy danh sách tất cả sự kiện đẩy xuống đơn vị (bao gồm cả HTTT và HTSK) theo kì học
    
    Query: semesterId - id kỳ học cần lọc.

    Quyền xem: VPĐ hoặc ADMIN
    """
    return await service.get_all_unit_events_by_semester_id(semester_id, skip=skip, limit=limit)

@router.get("/my", response_model=List[UnitEventResponseByUnitId], dependencies=[Depends(require_staff)])
async def Get_My_Unit_Events_By_Semester(
    semester_id: PydanticObjectId = Query(..., alias="semesterId"),
    current_user: TokenData = Depends(require_staff),
    service: UnitEventService = Depends(get_unit_event_service),
) -> List[UnitEventResponseByUnitId]:
    """
    Lấy danh sách sự kiện đẩy xuống đơn vị của tôi theo kỳ học

    Query: semesterId - id kỳ học cần lọc.

    Quyền xem: Quản lý đơn vị
    """
    return await service.get_unit_events_by_unit_id(current_user.sub, semester_id)


@router.get("/{event_id}", response_model=UnitEventResponse, dependencies=[Depends(require_manager)])
async def Get_Unit_Event_By_Id(
    event_id: PydanticObjectId,
    service: UnitEventService = Depends(get_unit_event_service),
) -> UnitEventResponse:
    """
    Lấy sự kiện đẩy xuống đơn vị theo id
    
    Quyền xem: VPĐ hoặc ADMIN hoặc STAFF
    """
    return await service.get_unit_event_by_id(event_id)

@router.put("/{event_id}", response_model=BaseResponse, dependencies=[Depends(require_manager)])
async def Update_Unit_Event(
    event_id: PydanticObjectId,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    point: Optional[float] = Form(None),
    listUnitId: Optional[str] = Form(None),
    semester_id: Optional[str] = Form(None),
    _ = Depends(require_manager),
    service: UnitEventService = Depends(get_unit_event_service),
) -> BaseResponse:
    from decimal import Decimal
    
    update_data = {}
    if title is not None: update_data["title"] = title
    if description is not None: update_data["description"] = description
    if point is not None: update_data["point"] = Decimal(str(point))
    
    if listUnitId:
        update_data["listUnitId"] = json.loads(listUnitId)
    
    if semester_id:
        update_data["semesterId"] = PydanticObjectId(semester_id)
        
    data = UnitEventUpdate(**update_data)
    
    return await service.update_unit_event(event_id, data)

@router.delete("/{event_id}", response_model=BaseResponse, dependencies=[Depends(require_manager)])
async def Delete_Unit_Event(
    event_id: PydanticObjectId,
    _ = Depends(require_manager),
    service: UnitEventService = Depends(get_unit_event_service),
) -> BaseResponse:
    """
    Xóa mềm sự kiện đẩy xuống đơn vị theo id
    
    Quyền xóa: VPĐ hoặc ADMIN
    """
    return await service.delete_unit_event(event_id)