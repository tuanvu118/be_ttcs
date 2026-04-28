from datetime import datetime, timezone

from beanie import PydanticObjectId

from exceptions import ErrorCode, app_exception
from repositories.event_registration_repo import EventRegistrationRepository
from repositories.public_event_repo import PublicEventRepository
from repositories.semester_repo import SemesterRepo
from repositories.unit_event_repo import UnitEventRepo
from repositories.user_unit_repo import UserUnitRepo
from repositories.user_repo import UserRepo
from schemas.event_registration import (
    EventRegistrationResponse,
    UnitEventRegistrationResponse,
    EventRegistrationUserResponse,
    MyEventRegistrationResponse,
    MyEventDetailResponse,
)


class EventRegistrationService:

    # -------------------------
    # VALIDATE FORM
    # -------------------------
    @staticmethod
    def _validate_answers(event, answers):

        if not event.form_fields:
            return

        answer_map = {a.field_id: a.value for a in answers}

        for field in event.form_fields:

            if field.required and (field.id not in answer_map or not str(answer_map[field.id]).strip()):
                app_exception(ErrorCode.MISSING_REQUIRED_FIELD, f"Trường '{field.label}' là bắt buộc")

            if field.id not in answer_map:
                continue

            value = str(answer_map[field.id])
            if not value.strip() and not field.required:
                continue

            if field.field_type in ["select", "radio"]:
                if value not in field.options:
                    app_exception(ErrorCode.INVALID_OPTION, f"Lựa chọn '{value}' không hợp lệ cho trường '{field.label}'")
            
            elif field.field_type == "checkbox":
                selected_options = [opt.strip() for opt in value.split(',')]
                for opt in selected_options:
                    if opt not in field.options:
                        app_exception(ErrorCode.INVALID_OPTION, f"Lựa chọn '{opt}' không hợp lệ cho trường '{field.label}'")
            
            elif field.field_type == "number":
                try:
                    float(value)
                except ValueError:
                    app_exception(ErrorCode.INVALID_FORM_FIELD, f"Trường '{field.label}' phải là một con số")
            
            elif field.field_type in ["text", "textarea"]:
                if len(value) > 1000:
                    app_exception(ErrorCode.INVALID_FORM_FIELD, f"Câu trả lời cho '{field.label}' không được vượt quá 1000 ký tự")

    # -------------------------
    # PUBLIC EVENT REGISTER
    # -------------------------
    @staticmethod
    async def register_public_event(
        event_id: PydanticObjectId,
        user_id: PydanticObjectId,
        answers,
    ) -> EventRegistrationResponse:

        event = await PublicEventRepository.get_by_id(event_id)

        if not event:
            app_exception(ErrorCode.EVENT_NOT_FOUND)

        now = datetime.now(timezone.utc)

        # Ensure registration times are aware
        reg_start = event.registration_start
        if reg_start.tzinfo is None:
            reg_start = reg_start.replace(tzinfo=timezone.utc)
        
        reg_end = event.registration_end
        if reg_end.tzinfo is None:
            reg_end = reg_end.replace(tzinfo=timezone.utc)

        if now < reg_start or now > reg_end:
            app_exception(ErrorCode.REGISTRATION_CLOSED)

        existed = await EventRegistrationRepository.get_by_event_and_user(
            event_id,
            user_id,
        )

        if existed:
            app_exception(ErrorCode.ALREADY_REGISTERED)

        # Check for overbooking
        current_count = await EventRegistrationRepository.count_by_event(event_id)
        if event.max_participants > 0 and current_count >= event.max_participants:
            app_exception(ErrorCode.EVENT_FULL)

        EventRegistrationService._validate_answers(event, answers)

        registration = await EventRegistrationRepository.create(
            {
                "event_id": event_id,
                "event_type": "public",
                "user_id": user_id,
                "answers": [a.model_dump() for a in answers],
                "registered_at": now,
            }
        )

        reg_at = registration.registered_at
        if reg_at.tzinfo is None:
            registration.registered_at = reg_at.replace(tzinfo=timezone.utc)

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

        allowed_unit_ids = event.listUnitId or []
        if unit_id not in allowed_unit_ids:
            app_exception(ErrorCode.UNIT_NOT_ALLOWED)

        active_semester = await SemesterRepo().get_active()

        if not active_semester:
            app_exception(ErrorCode.ACTIVE_SEMESTER_NOT_FOUND)

        membership = await UserUnitRepo().get_active(
            user_id,
            unit_id,
            active_semester.id,
        )
        if not membership:
            app_exception(ErrorCode.USER_NOT_IN_UNIT)

        existed = await EventRegistrationRepository.get_by_event_and_user(
            event_id,
            user_id,
        )

        if existed:
            app_exception(ErrorCode.ALREADY_REGISTERED)

        registration = await EventRegistrationRepository.create(
            {
                "event_id": event_id,
                "event_type": "unit",
                "user_id": user_id,
                "registered_at": datetime.now(timezone.utc),
            }
        )
        reg_at = registration.registered_at
        if reg_at.tzinfo is None:
            reg_at = reg_at.replace(tzinfo=timezone.utc)
            
        return UnitEventRegistrationResponse(
            id=registration.id,
            event_id=registration.event_id,
            user_id=registration.user_id,
            unit_id=unit_id,
            registered_at=reg_at,
        )

    # -------------------------
    # CANCEL
    # -------------------------
    @staticmethod
    async def cancel(
        event_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ):

        deleted = await EventRegistrationRepository.delete_by_event_and_user(
            event_id,
            user_id,
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

        public_events = await PublicEventRepository.get_by_ids(event_ids)
        unit_events = await UnitEventRepo().get_by_ids(event_ids)

        event_map = {e.id: e for e in public_events + unit_events}

        result = []

        for r in registrations:

            event = event_map.get(r.event_id)

            if not event:
                continue

            reg_at = r.registered_at
            if reg_at.tzinfo is None:
                reg_at = reg_at.replace(tzinfo=timezone.utc)

            result.append(
                MyEventRegistrationResponse(
                    event_id=event.id,
                    title=event.title,
                    event_start=event.event_start,
                    registered_at=reg_at,
                )
            )

        return result

    @staticmethod
    async def get_event_registrations(
        event_id: PydanticObjectId,
    ) -> list[EventRegistrationUserResponse]:

        registrations = await EventRegistrationRepository.get_by_event(event_id)
        if not registrations:
            return []

        user_ids = [r.user_id for r in registrations]

        users = await UserRepo().get_by_ids(user_ids)

        user_map = {u.id: u for u in users}

        result = []

        for r in registrations:

            user = user_map.get(r.user_id)

            if not user:
                continue

            reg_at = r.registered_at
            if reg_at.tzinfo is None:
                reg_at = reg_at.replace(tzinfo=timezone.utc)

            result.append(
                EventRegistrationUserResponse(
                    user_id=user.id,
                    full_name=user.full_name,
                    student_id=user.student_id,
                    answers=r.answers,
                    registered_at=reg_at,
                    checked_in=getattr(r, "checked_in", False),
                )

            )

        return result

    @staticmethod
    async def get_my_event_detail(
        event_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> MyEventDetailResponse:

        registration = await EventRegistrationRepository.get_by_event_and_user(
            event_id,
            user_id,
        )

        if not registration:
            app_exception(ErrorCode.REGISTRATION_NOT_FOUND)

        reg_at = registration.registered_at
        if reg_at.tzinfo is None:
            reg_at = reg_at.replace(tzinfo=timezone.utc)

        return MyEventDetailResponse(
            event_id=registration.event_id,
            answers=registration.answers,
            registered_at=reg_at,
            checked_in=getattr(registration, 'checked_in', False),
        )
