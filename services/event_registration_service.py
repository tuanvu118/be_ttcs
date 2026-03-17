from datetime import datetime, timezone

from beanie import PydanticObjectId

from exceptions import ErrorCode, app_exception
from repositories.event_registration_repo import EventRegistrationRepository
from repositories.public_event_repo import PublicEventRepository
from repositories.unit_event_repo import UnitEventRepo
from repositories.user_repo import UserRepo
from repositories.user_role_repo import UserRoleRepo
from repositories.unit_event_assigned_units_repo import UnitEventAssignedUnitsRepo
from schemas.event_registration import (
    EventRegistrationResponse,
    EventRegistrationUserResponse,
    MyEventDetailResponse,
    MyEventRegistrationResponse, UnitEventRegistrationResponse,
)


class EventRegistrationService:
    @staticmethod
    async def register_public_event(
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
    async def register_unit_event(
            event_id: PydanticObjectId,
            user_id: PydanticObjectId,
            unit_id: PydanticObjectId,
    ) -> UnitEventRegistrationResponse:

        event = await UnitEventRepo().get_by_id(event_id)
        if not event:
            app_exception(ErrorCode.EVENT_NOT_FOUND)

        user = await UserRepo().get_by_id(user_id)
        if not user:
            app_exception(ErrorCode.USER_NOT_FOUND)

        units = await UnitEventAssignedUnitsRepo().list_by_event_id(event_id)

        unit_ids = [u.unitId for u in units]

        if unit_id not in unit_ids:
            app_exception(ErrorCode.UNIT_NOT_ALLOWED)

        roles = await UserRoleRepo().list_active_by_user_and_unit(user_id, unit_id)
        if not roles:
            app_exception(ErrorCode.USER_NOT_IN_UNIT)

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
        return UnitEventRegistrationResponse(
            id=registration.id,
            event_id=registration.event_id,
            user_id=registration.user_id,
            unit_id=unit_id,
            registered_at=registration.registered_at,
        )

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

        event_ids = [registration.event_id for registration in registrations]
        events = await PublicEventRepository.get_by_ids(event_ids)
        event_map = {event.id: event for event in events}

        result = []
        for registration in registrations:
            event = event_map.get(registration.event_id)
            if not event:
                continue

            result.append(
                MyEventRegistrationResponse(
                    event_id=event.id,
                    title=event.title,
                    event_start=event.event_start,
                    registered_at=registration.registered_at,
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

        user_ids = [registration.user_id for registration in registrations]
        users = await UserRepo.get_by_ids(user_ids)
        user_map = {user.id: user for user in users}

        result = []
        for registration in registrations:
            user = user_map.get(registration.user_id)
            if not user:
                continue

            result.append(
                EventRegistrationUserResponse(
                    user_id=user.id,
                    full_name=user.full_name,
                    student_id=user.student_id,
                    registered_at=registration.registered_at,
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
