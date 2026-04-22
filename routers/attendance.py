from typing import List

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Path, Request, status

from schemas.attendance import (
    AttendanceRead,
    QRScanQueuedResponse,
    QRScanRequest,
    QRSessionOpenRequest,
    QRSessionOpenResponse,
    QRSessionRead,
)
from schemas.auth import TokenData
from security import require_admin_or_manager_global, require_user
from services.qr_attendance_service import QRAttendanceService

router = APIRouter(prefix="/attendance", tags=["QR Attendance"])


@router.post(
    "/events/{event_id}/sessions",
    response_model=QRSessionOpenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def open_qr_session(
    request_body: QRSessionOpenRequest,
    event_id: PydanticObjectId = Path(...),
    current_user: TokenData = Depends(require_admin_or_manager_global),
):
    return await QRAttendanceService.open_session(
        event_id=event_id,
        actor_id=PydanticObjectId(current_user.sub),
        request=request_body,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=QRSessionRead,
)
async def get_qr_session(
    session_id: str,
    _: TokenData = Depends(require_admin_or_manager_global),
):
    return await QRAttendanceService.get_session(session_id)


@router.post(
    "/sessions/{session_id}/close",
    response_model=QRSessionRead,
)
async def close_qr_session(
    session_id: str,
    current_user: TokenData = Depends(require_admin_or_manager_global),
):
    return await QRAttendanceService.close_session(
        session_id=session_id,
        actor_id=PydanticObjectId(current_user.sub),
    )


@router.post(
    "/scan",
    response_model=QRScanQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def scan_qr_code(
    request_body: QRScanRequest,
    request: Request,
    current_user: TokenData = Depends(require_user),
):
    return await QRAttendanceService.submit_scan(
        current_user_id=PydanticObjectId(current_user.sub),
        request=request_body,
        source_ip=request.client.host if request.client else None,
    )


@router.get(
    "/events/{event_id}/records",
    response_model=List[AttendanceRead],
)
async def list_attendance_records(
    event_id: PydanticObjectId = Path(...),
    _: TokenData = Depends(require_admin_or_manager_global),
):
    return await QRAttendanceService.list_attendances(event_id=event_id)
