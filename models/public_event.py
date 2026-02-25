from datetime import datetime, timezone
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field


class PublicEvent(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    title: str
    description: str
    image_url: Optional[str]=None
    point: int = 0
    registration_start: datetime
    registration_end: datetime
    event_start: datetime
    event_end: datetime
    auto_add_report: bool = False
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "public_events"