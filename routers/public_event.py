from typing import List, Optional

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Form, UploadFile, File, status, HTTPException, Query
from pydantic import ValidationError
import json
from schemas.public_event import PublicEventCreate, PublicEventRead, PublicEventUpdate, PublicEventPaginationResponse
from security import require_manager, require_user
from services.public_event_service import PublicEventService


router = APIRouter(prefix="/events", tags=["Public Events"])


@router.post("/", response_model=PublicEventRead)
async def create_event(
    title: str = Form(...),
    description: str = Form(...),
    point: float = Form(0),
    registration_start: str = Form(...),
    registration_end: str = Form(...),
    event_start: str = Form(...),
    event_end: str = Form(...),
    form_fields: str = Form("[]"),
    location: Optional[str] = Form(None),
    max_participants: int = Form(0),
    semester_id: Optional[str] = Form(None),
    image: UploadFile = File(None),
    _=Depends(require_manager),

):
    from datetime import datetime
    
    # Parse form_fields string to list of dicts
    fields_list = json.loads(form_fields)
    
    try:
        data = PublicEventCreate(
            title=title,
            description=description,
            point=point,
            registration_start=datetime.fromisoformat(registration_start),
            registration_end=datetime.fromisoformat(registration_end),
            event_start=datetime.fromisoformat(event_start),
            event_end=datetime.fromisoformat(event_end),
            location=location,
            max_participants=max_participants,
            form_fields=fields_list,
            semester_id=PydanticObjectId(semester_id) if semester_id else None
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())

    
    return await PublicEventService.create_event(data, image)


@router.get("/", response_model=PublicEventPaginationResponse)
async def get_events(
    semester_id: Optional[PydanticObjectId] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    _=Depends(require_manager),
):
    return await PublicEventService.get_events(semester_id=semester_id, skip=skip, limit=limit)


@router.get("/valid", response_model=PublicEventPaginationResponse)
async def get_valid_events(
    semester_id: Optional[PydanticObjectId] = Query(None, alias="semester_id"),
    search: Optional[str] = Query(None),
    time_filter: Optional[str] = Query(None, alias="timeFilter"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    return await PublicEventService.get_valid_events(
        semester_id=semester_id,
        search=search,
        time_filter=time_filter,
        skip=skip,
        limit=limit
    )


@router.get("/{event_id}", response_model=PublicEventRead)
async def get_detail_event(
    event_id: PydanticObjectId,
):
    return await PublicEventService.get_event_by_id(event_id)


@router.put("/{event_id}", response_model=PublicEventRead)
async def update_event(
    event_id: PydanticObjectId,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    point: Optional[float] = Form(None),
    registration_start: Optional[str] = Form(None),
    registration_end: Optional[str] = Form(None),
    event_start: Optional[str] = Form(None),
    event_end: Optional[str] = Form(None),
    form_fields: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    max_participants: Optional[int] = Form(None),
    semester_id: Optional[str] = Form(None),
    image: UploadFile = File(None),
    _=Depends(require_manager),

):
    from datetime import datetime
    
    update_data = {}
    if title is not None: update_data["title"] = title
    if description is not None: update_data["description"] = description
    if point is not None: update_data["point"] = point
    if location is not None: update_data["location"] = location
    if max_participants is not None: update_data["max_participants"] = max_participants

    
    if registration_start: update_data["registration_start"] = datetime.fromisoformat(registration_start)
    if registration_end: update_data["registration_end"] = datetime.fromisoformat(registration_end)
    if event_start: update_data["event_start"] = datetime.fromisoformat(event_start)
    if event_end: update_data["event_end"] = datetime.fromisoformat(event_end)
    
    if form_fields:
        update_data["form_fields"] = json.loads(form_fields)
    
    if semester_id:
        update_data["semester_id"] = PydanticObjectId(semester_id)
        
    try:
        data = PublicEventUpdate(**update_data)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())
    return await PublicEventService.update_event(event_id, data, image)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: PydanticObjectId,
    _=Depends(require_manager),
):
    await PublicEventService.delete_event(event_id)

