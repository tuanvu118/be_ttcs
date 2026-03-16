from datetime import datetime
from typing import List

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
    async def get_all():
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
    async def get_valid_events(now: datetime):
        return await PublicEvent.find({
            "$or": [
                {"registration_start": {"$gt": now}},
                {
                    "registration_start": {"$lte": now},
                    "registration_end": {"$gte": now},
                },
                {
                    "event_start": {"$lte": now},
                    "event_end": {"$gte": now},
                }
            ]
        }).sort("event_start").to_list()