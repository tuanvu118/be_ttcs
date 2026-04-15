from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import List, Optional
from schemas.event_registration import FormAnswer



class EventRegistration(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    event_id: PydanticObjectId
    event_type: str = "public"
    user_id: PydanticObjectId
    answers: List[FormAnswer] = Field(default_factory=list)
    registered_at: datetime
    checked_in: bool = False


    class Settings:
        name = "event_registrations"