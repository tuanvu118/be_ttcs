from typing import List

from fastapi import APIRouter, Depends, Path, status, Header
from beanie import PydanticObjectId

from schemas.auth import TokenData
from security import require_user, require_admin
from services.event_registration_service import EventRegistrationService
from schemas.event_registration import (
    EventRegistrationResponse,
    EventRegistrationUserResponse,
    MyEventRegistrationResponse, MyEventDetailResponse,
)


router = APIRouter(prefix="/api/events", tags=["Event Registration"])

@router.post(
    "/{event_id}/register_public_event",
    response_model=EventRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_public_event(
    event_id: PydanticObjectId = Path(...),
    current_user: TokenData = Depends(require_user),
):
    return await EventRegistrationService.register_public_event(
        event_id=event_id,
        user_id=PydanticObjectId(current_user.sub)
    )

async def register_unit_event(
    event_id: PydanticObjectId = Path(...),
    current_user: TokenData = Depends(require_user),
    x_unit_id: PydanticObjectId = Header(..., alias="X-Unit-Id"),
):
    return await EventRegistrationService.register_unit_event(
        event_id=event_id,
        user_id=PydanticObjectId(current_user.sub),
        unit_id=x_unit_id
    )


@router.delete(
    "/{event_id}/register",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_registration(
    event_id: PydanticObjectId = Path(...),
    current_user: TokenData = Depends(require_user),
):
    await EventRegistrationService.cancel(
        event_id=event_id,
        user_id=PydanticObjectId(current_user.sub)
    )

@router.get(
    "/me/registrations",
    response_model=List[MyEventRegistrationResponse],
)
async def get_my_registrations(
    current_user: TokenData = Depends(require_user),
):
    return await EventRegistrationService.get_my_registrations(
        user_id=PydanticObjectId(current_user.sub)
    )

@router.get(
    "/{event_id}/registrations",
    response_model=List[EventRegistrationUserResponse],
    dependencies=[Depends(require_admin)]
)
async def get_event_registrations(
    event_id: PydanticObjectId = Path(...)
):
    return await EventRegistrationService.get_event_registrations(
        event_id=event_id
    )

@router.get(
    "/{event_id}/my-registration",
    response_model=MyEventDetailResponse,
)
async def get_my_event_detail(
    event_id: PydanticObjectId = Path(...),
    current_user: TokenData = Depends(require_user),
):
    return await EventRegistrationService.get_my_event_detail(
        event_id=event_id,
        user_id=PydanticObjectId(current_user.sub)
    )