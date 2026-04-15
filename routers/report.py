from typing import List, Optional
from schemas.auth import TokenData
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Header, status, Body
from fastapi.responses import StreamingResponse
from schemas.report import (
    InternalEventCreate,
    InternalEventRead,
    InternalEventUpdate,
    ReportDetail,
    ReportSummary,
)
from security import get_current_user, require_manager, require_staff
from services.report import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/all",
    response_model=List[ReportSummary],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_manager)],
)
async def get_all_reports():
    return await ReportService.get_all_reports()


@router.get(
    "/",
    response_model=List[ReportSummary],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_staff)],
)
async def get_reports(
    x_unit_id: PydanticObjectId = Header(..., alias="X-Unit-Id"),
):
    return await ReportService.get_reports_by_unit(x_unit_id)


@router.get(
    "/{report_id}",
    response_model=ReportDetail,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_report_detail(
    report_id: PydanticObjectId,
    current_user: TokenData = Depends(get_current_user)
):
    return await ReportService.get_report_detail(report_id, current_user)

@router.post(
    "/{report_id}/internal-events",
    response_model=InternalEventRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_staff)],
)
async def create_internal_event(
    report_id: PydanticObjectId,
    data: InternalEventCreate,
):
    return await ReportService.add_internal_event(
        report_id,
        data,
    )


@router.put(
    "/{report_id}/internal-events/{event_id}",
    response_model=InternalEventRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_staff)],
)
async def update_internal_event(
    report_id: PydanticObjectId,
    event_id: PydanticObjectId,
    data: InternalEventUpdate,
):
    return await ReportService.update_internal_event(
        report_id,
        event_id,
        data,
    )


@router.delete(
    "/{report_id}/internal-events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_staff)],
)
async def delete_internal_event(
    report_id: PydanticObjectId,
    event_id: PydanticObjectId,
):
    await ReportService.delete_internal_event(
        report_id,
        event_id,
    )
@router.post(
    "/{report_id}/submit",
    response_model=ReportDetail,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_staff)],
)
async def submit_report(
    report_id: PydanticObjectId,
):
    return await ReportService.submit_report(report_id)


@router.post(
    "/{report_id}/status",
    response_model=ReportDetail,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_manager)],
)
async def update_report_status(
    report_id: PydanticObjectId,
    status: str = Body(..., embed=True),
    note: Optional[str] = Body(None, embed=True),
):
    return await ReportService.update_report_status(report_id, status, note)


@router.get(
    "/export/summary",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_manager)],
)
async def export_summary_excel():
    buffer = await ReportService.export_summary_excel()
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=report_summary.xlsx"}
    )


@router.get(
    "/{report_id}/export/detail",
    status_code=status.HTTP_200_OK,
)
async def export_detailed_excel(report_id: PydanticObjectId):
    buffer = await ReportService.export_detailed_excel(report_id)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=report_detail_{report_id}.xlsx"}
    )
