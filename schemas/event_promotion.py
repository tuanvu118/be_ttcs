from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from beanie import PydanticObjectId

class EventTimeSchema(BaseModel):
    start: datetime
    end: datetime

class OrganizationInfoSchema(BaseModel):
    id: str
    name: str

class EventPromotionBase(BaseModel):
    title: str
    description: str
    time: Optional[EventTimeSchema] = None
    semester_id: Optional[PydanticObjectId] = None
    image_url: Optional[str] = None
    external_links: List[str] = []

class EventPromotionCreate(EventPromotionBase):
    pass

class EventPromotionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time: Optional[EventTimeSchema] = None
    image_url: Optional[str] = None
    external_links: Optional[List[str]] = None

class EventPromotionStatusUpdate(BaseModel):
    status: str  # DA_DUYET | TU_CHOI
    rejected_reason: Optional[str] = None

class EventPromotionRead(EventPromotionBase):
    id: PydanticObjectId
    status: str
    organization: Optional[OrganizationInfoSchema] = None
    rejected_reason: Optional[str] = None
    unit_id: Optional[PydanticObjectId] = None
    semester_id: Optional[PydanticObjectId] = None
    created_at: datetime
    updated_at: datetime

class EventPromotionPaginationResponse(BaseModel):
    items: List[EventPromotionRead]
    total: int
