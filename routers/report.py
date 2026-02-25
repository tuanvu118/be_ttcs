
from typing import List
from fastapi import APIRouter, Depends, Header, status
from beanie import PydanticObjectId

from schemas.auth import TokenData
from security import require_manager, require_staff, get_current_user
from services.report import ReportService
from schemas.report import (
    ReportSummary,
    ReportDetail,
    InternalEventCreate,
    InternalEventUpdate,
    InternalEventRead,
    ReportCreate,
    ReportUpdate,
)

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)

@router.get(
    "/all",
    response_model=List[ReportSummary],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_manager)]
)
async def get_all_reports():
    return await ReportService.get_all_reports()


@router.get(
    "/",
    response_model=List[ReportSummary],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_staff)]
)
async def get_reports(
    x_don_vi_id: PydanticObjectId = Header(..., alias="X-DonVi-Id"),
):
    return await ReportService.get_reports_by_unit(x_don_vi_id)


@router.get(
    "/{report_id}",
    response_model=ReportDetail,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_staff)]
)
@router.get(
    "/{report_id}",
    response_model=ReportDetail,
    status_code=status.HTTP_200_OK,
)
async def get_report_detail(
    report_id: PydanticObjectId,
    current_user: TokenData = Depends(get_current_user),
):
    return await ReportService.get_report_detail(
        report_id=report_id,
        current_user=current_user,
    )

@router.post(
    "/",
    response_model=ReportSummary,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_staff)]
)
async def create_report(
    data: ReportCreate,
    x_don_vi_id: PydanticObjectId = Header(..., alias="X-DonVi-Id"),
):
    return await ReportService.create_report(
        unit_id=x_don_vi_id,
        data=data
    )


@router.put(
    "/{report_id}",
    response_model=ReportSummary,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_staff)]
)
async def update_report(
    report_id: PydanticObjectId,
    data: ReportUpdate,
):
    return await ReportService.update_report(
        report_id,
        data,
    )


@router.post(
    "/{report_id}/internal-events",
    response_model=InternalEventRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_staff)]
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
    dependencies=[Depends(require_staff)]
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
    dependencies=[Depends(require_staff)]
)
async def delete_internal_event(
    report_id: PydanticObjectId,
    event_id: PydanticObjectId,
):
    await ReportService.delete_internal_event(
        report_id,
        event_id,
    )