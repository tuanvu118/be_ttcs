from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import Field


class EventRegistration(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    event_id: PydanticObjectId
    user_id: PydanticObjectId
    registered_at: datetime
    checked_in: bool = False

    class Settings:
        name = "event_registrations"