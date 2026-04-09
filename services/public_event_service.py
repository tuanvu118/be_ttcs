from datetime import datetime, timezone
from typing import Optional

from beanie import PydanticObjectId

from exceptions import ErrorCode, app_exception
from schemas.public_event import PublicEventCreate, PublicEventUpdate
from repositories.public_event_repo import PublicEventRepository
from repositories.semester_repo import SemesterRepo

class PublicEventService:
    @staticmethod
    def _validate_time(
        registration_start,
        registration_end,
        event_start,
        event_end,
    ):
        if registration_start >= registration_end:
            app_exception(ErrorCode.INVALID_REGISTRATION_TIME)

        if event_start < registration_end:
            app_exception(ErrorCode.EVENT_MUST_START_AFTER_REGISTRATION)

        if event_start >= event_end:
            app_exception(ErrorCode.INVALID_EVENT_TIME)

    #validate form fields
    @staticmethod
    def _validate_form_fields(form_fields):
        if not form_fields:
            return

        ids = set()

        for field in form_fields:
            if field.id in ids:
                app_exception(ErrorCode.INVALID_FORM_FIELD)

            ids.add(field.id)

            if field.field_type in ["select", "radio", "checkbox"]:
                if not field.options:
                    app_exception(ErrorCode.INVALID_FORM_FIELD)
    @staticmethod
    async def create_event(data: PublicEventCreate):

        PublicEventService._validate_time(
            data.registration_start,
            data.registration_end,
            data.event_start,
            data.event_end,
        )

        # validate form
        PublicEventService._validate_form_fields(data.form_fields)
        payload = data.model_dump()
        payload["created_at"] = datetime.now(timezone.utc)
        semester = await SemesterRepo().get_active()

        if not semester:
            raise ValueError("No active semester")

        payload["semester_id"] = semester.id
        return await PublicEventRepository.create(payload)

    @staticmethod
    async def get_events(semester_id: Optional[PydanticObjectId] = None):
        return await PublicEventRepository.get_all(semester_id=semester_id)

    @staticmethod
    async def get_event_by_id(event_id: PydanticObjectId):
        event = await PublicEventRepository.get_by_id(event_id)
        if not event:
             app_exception(ErrorCode.EVENT_NOT_FOUND)
        return event

    @staticmethod
    async def update_event(event_id: PydanticObjectId, data: PublicEventUpdate):

        event = await PublicEventRepository.get_by_id(event_id)
        if not event:
            app_exception(ErrorCode.EVENT_NOT_FOUND)

        update_data = data.model_dump(exclude_unset=True)

        merged_data = {
            "registration_start": update_data.get(
                "registration_start", event.registration_start
            ),
            "registration_end": update_data.get(
                "registration_end", event.registration_end
            ),
            "event_start": update_data.get(
                "event_start", event.event_start
            ),
            "event_end": update_data.get(
                "event_end", event.event_end
            ),
        }

        PublicEventService._validate_time(
            merged_data["registration_start"],
            merged_data["registration_end"],
            merged_data["event_start"],
            merged_data["event_end"],
        )

        # validate form_fields nếu có update
        if "form_fields" in update_data:
            PublicEventService._validate_form_fields(update_data["form_fields"])

        return await PublicEventRepository.update(event_id, update_data)

    @staticmethod
    async def get_valid_events(semester_id: Optional[PydanticObjectId] = None):
        now = datetime.now(timezone.utc)
        return await PublicEventRepository.get_valid_events(now, semester_id=semester_id)