from fastapi import APIRouter, Depends
from typing import List
from beanie import PydanticObjectId

from schemas.public_event import (
    PublicEventCreate,
    PublicEventRead,
    PublicEventUpdate,
)
from security import require_manager, require_user
from services.public_event_service import PublicEventService


router = APIRouter(prefix="/api/events", tags=["Public Events"])

@router.post("/", response_model=PublicEventRead)
async def create_event(
    data: PublicEventCreate,
    _ = Depends(require_manager),
):
    return await PublicEventService.create_event(data)


@router.get("/", response_model=List[PublicEventRead])
async def get_events(
    _ = Depends(require_manager),
):
    return await PublicEventService.get_events()

@router.get("/valid", response_model=List[PublicEventRead])
async def get_valid_events(
    _ = Depends(require_user)
):
    return await PublicEventService.get_valid_events()


@router.get("/{event_id}", response_model=PublicEventRead)
async def get_detail_event(event_id: PydanticObjectId,
                    _=Depends(require_user)
                    ):
    return await PublicEventService.get_event_by_id(event_id)


@router.put("/{event_id}", response_model=PublicEventRead)
async def update_event(
    event_id: PydanticObjectId,
    data: PublicEventUpdate,
    _ = Depends(require_manager),
):
    return await PublicEventService.update_event(event_id, data)