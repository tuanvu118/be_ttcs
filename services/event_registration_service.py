from datetime import datetime, timezone
from beanie import PydanticObjectId

from exceptions import app_exception, ErrorCode
from repositories.public_event_repo import PublicEventRepository
from repositories.event_registration_repo import EventRegistrationRepository
from repositories.user_repo import UserRepo

from schemas.event_registration import (
    EventRegistrationResponse,
    EventRegistrationUserResponse,
    MyEventRegistrationResponse, MyEventDetailResponse,
)

class EventRegistrationService:

    @staticmethod
    async def register(
        event_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> EventRegistrationResponse:

        event = await PublicEventRepository.get_by_id(event_id)
        if not event:
            app_exception(ErrorCode.EVENT_NOT_FOUND)

        existed = await EventRegistrationRepository.get_by_event_and_user(
            event_id, user_id
        )
        if existed:
            app_exception(ErrorCode.ALREADY_REGISTERED)

        registration = await EventRegistrationRepository.create(
            {
                "event_id": event_id,
                "user_id": user_id,
                "registered_at": datetime.now(timezone.utc),
            }
        )

        return EventRegistrationResponse.model_validate(registration)

    @staticmethod
    async def cancel(
        event_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> None:

        deleted = await EventRegistrationRepository.delete_by_event_and_user(
            event_id, user_id
        )

        if not deleted:
            app_exception(ErrorCode.REGISTRATION_NOT_FOUND)

    @staticmethod
    async def get_my_registrations(
        user_id: PydanticObjectId,
    ) -> list[MyEventRegistrationResponse]:

        registrations = await EventRegistrationRepository.get_by_user(user_id)

        if not registrations:
            return []

        event_ids = [r.event_id for r in registrations]

        events = await PublicEventRepository.get_by_ids(event_ids)

        event_map = {e.id: e for e in events}

        result = []

        for r in registrations:
            event = event_map.get(r.event_id)
            if not event:
                continue

            result.append(
                MyEventRegistrationResponse(
                    event_id=event.id,
                    title=event.title,
                    event_start=event.event_start,
                    registered_at=r.registered_at,
                )
            )

        return result

    @staticmethod
    async def get_event_registrations(
        event_id: PydanticObjectId,
    ) -> list[EventRegistrationUserResponse]:

        event = await PublicEventRepository.get_by_id(event_id)
        if not event:
            app_exception(ErrorCode.EVENT_NOT_FOUND)

        registrations = await EventRegistrationRepository.get_by_event(event_id)

        if not registrations:
            return []

        user_ids = [r.user_id for r in registrations]

        users = await UserRepo.get_by_ids(user_ids)

        user_map = {u.id: u for u in users}

        result = []

        for r in registrations:
            user = user_map.get(r.user_id)
            if not user:
                continue

            result.append(
                EventRegistrationUserResponse(
                    user_id=user.id,
                    full_name=user.full_name,
                    student_code=user.student_code,
                    registered_at=r.registered_at,
                )
            )

        return result

    @staticmethod
    async def get_my_event_detail(
            event_id: PydanticObjectId,
            user_id: PydanticObjectId,
    ) -> MyEventDetailResponse:

        event = await PublicEventRepository.get_by_id(event_id)
        if not event:
            app_exception(ErrorCode.EVENT_NOT_FOUND)

        registration = await EventRegistrationRepository.get_by_event_and_user(
            event_id, user_id
        )

        if not registration:
            app_exception(ErrorCode.REGISTRATION_NOT_FOUND)

        return MyEventDetailResponse(
            event_id=event.id,
            title=event.title,
            description=event.description,
            event_start=event.event_start,
            event_end=event.event_end,
            registered_at=registration.registered_at,
        )