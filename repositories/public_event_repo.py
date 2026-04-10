from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId

from models.public_event import PublicEvent


class PublicEventRepository:

    @staticmethod
    async def create(data: dict) -> PublicEvent:
        event = PublicEvent(**data)
        await event.insert()
        return event

    @staticmethod
    async def get_by_id(event_id: PydanticObjectId):
        return await PublicEvent.get(event_id)

    @staticmethod
    async def get_all(semester_id: Optional[PydanticObjectId] = None):
        if semester_id:
            return await PublicEvent.find({"semester_id": semester_id}).to_list()
        return await PublicEvent.find_all().to_list()

    @staticmethod
    async def update(event_id: PydanticObjectId, data: dict):
        event = await PublicEvent.get(event_id)
        if not event:
            return None

        await event.update({"$set": data})

        return await PublicEvent.get(event_id)

    @staticmethod
    async def get_by_ids(
            ids: List[PydanticObjectId]
    ) -> List[PublicEvent]:

        if not ids:
            return []

        return await PublicEvent.find(
            {"_id": {"$in": ids}}
        ).to_list()

    @staticmethod
    async def get_valid_events(now: datetime, semester_id: Optional[PydanticObjectId] = None):
        query = {
            "event_end": {"$gte": now}
        }

        if semester_id:
            query["semester_id"] = semester_id
            
        return await PublicEvent.find(query).sort("event_start").to_list()

    @staticmethod
    async def delete(event_id: PydanticObjectId):
        event = await PublicEvent.get(event_id)
        if event:
            await event.delete()
            return True
        return False