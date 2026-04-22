from datetime import datetime, timezone

from beanie import PydanticObjectId

from configs.redis_config import get_redis
from configs.settings import (
    QR_CHECKIN_LOCK_TTL_SECONDS,
    QR_DUPLICATE_COMPLETED_TTL_SECONDS,
)
from models.attendance import Attendance
from models.audit_log import AuditLog
from repositories.attendance_repo import AttendanceRepository
from repositories.audit_log_repo import AuditLogRepository
from repositories.event_registration_repo import EventRegistrationRepository
from repositories.public_event_repo import PublicEventRepository
from schemas.attendance import CheckInMessage


class AttendanceWorkerService:
    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _ensure_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    async def _acquire_lock(lock_key: str, token: str) -> bool:
        redis = get_redis()
        acquired = await redis.set(
            lock_key,
            token,
            ex=QR_CHECKIN_LOCK_TTL_SECONDS,
            nx=True,
        )
        return bool(acquired)

    @staticmethod
    async def _release_lock(lock_key: str, token: str) -> None:
        redis = get_redis()
        current_token = await redis.get(lock_key)
        if current_token == token:
            await redis.delete(lock_key)

    @staticmethod
    async def _set_completed_duplicate_marker(
        duplicate_key: str,
        event_end: datetime | None,
        request_id: str,
    ) -> None:
        redis = get_redis()
        now = AttendanceWorkerService._utc_now()
        ttl_seconds = QR_DUPLICATE_COMPLETED_TTL_SECONDS
        normalized_event_end = AttendanceWorkerService._ensure_utc(event_end)
        if normalized_event_end is not None:
            ttl_seconds = max(
                ttl_seconds,
                int((normalized_event_end - now).total_seconds())
                + QR_DUPLICATE_COMPLETED_TTL_SECONDS,
            )
        await redis.set(
            duplicate_key,
            f"processed:{request_id}",
            ex=max(1, ttl_seconds),
        )

    @staticmethod
    async def process_checkin(message: CheckInMessage) -> None:
        event_id = PydanticObjectId(message.event_id)
        user_id = PydanticObjectId(message.user_id)
        lock_key = f"checkin_lock:{user_id}:{event_id}"
        lock_token = message.request_id
        duplicate_key = message.duplicate_key

        if not await AttendanceWorkerService._acquire_lock(lock_key, lock_token):
            return

        redis = get_redis()
        try:
            if await AttendanceRepository.exists_by_event_and_user(event_id, user_id):
                event = await PublicEventRepository.get_by_id(event_id)
                event_end = event.event_end if event else None
                await AttendanceWorkerService._set_completed_duplicate_marker(
                    duplicate_key=duplicate_key,
                    event_end=event_end,
                    request_id=message.request_id,
                )
                return

            registration = await EventRegistrationRepository.get_by_event_and_user(
                event_id,
                user_id,
            )
            if not registration:
                await redis.delete(duplicate_key)
                return

            event = await PublicEventRepository.get_by_id(event_id)
            event_end = event.event_end if event else None

            attendance = Attendance(
                event_id=event_id,
                event_type=message.event_type,
                user_id=user_id,
                session_id=message.session_id,
                sequence=message.sequence,
                request_id=message.request_id,
                valid_from=message.valid_from,
                valid_until=message.valid_until,
                scanned_at=message.scanned_at,
                processed_at=AttendanceWorkerService._utc_now(),
                checkin_latitude=message.latitude,
                checkin_longitude=message.longitude,
                distance_meters=message.distance_meters,
                source="qr",
            )
            await AttendanceRepository.create(attendance)
            await EventRegistrationRepository.mark_checked_in(event_id, user_id)
            await AuditLogRepository.create(
                AuditLog(
                    action="attendance.checkin.completed",
                    actor_id=user_id,
                    event_id=event_id,
                    user_id=user_id,
                    target_type="attendance",
                    target_id=str(attendance.id),
                    request_id=message.request_id,
                    metadata={
                        "session_id": message.session_id,
                        "sequence": message.sequence,
                        "distance_meters": message.distance_meters,
                        "source_ip": message.source_ip,
                    },
                )
            )
            await AttendanceWorkerService._set_completed_duplicate_marker(
                duplicate_key=duplicate_key,
                event_end=event_end,
                request_id=message.request_id,
            )
        except Exception:
            await redis.delete(duplicate_key)
            raise
        finally:
            await AttendanceWorkerService._release_lock(lock_key, lock_token)
