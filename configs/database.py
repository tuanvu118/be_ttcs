from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

from configs.settings import DB_NAME, MONGO_URI
from models.attendance import Attendance
from models.audit_log import AuditLog
from models.event_registration import EventRegistration
from models.public_event import PublicEvent
from models.refresh_tokens import RefreshTokenSession
from models.report import Report
from models.roles import Role
from models.semester import Semester
from models.unit import Unit
from models.unit_event import UnitEvent
from models.unit_event_submission_members import UnitEventSubmissionMember
from models.unit_event_submissions import UnitEventSubmission
from models.user_unit import UserUnit
from models.users import User
from models.users_roles import UserRole
from models.event_promotion import EventPromotion

client = AsyncIOMotorClient(MONGO_URI)


async def _sync_attendance_indexes() -> None:
    collection = client[DB_NAME][Attendance.Settings.name]
    index_info = await collection.index_information()
    legacy_unique_index = "event_id_1_user_id_1"
    if legacy_unique_index in index_info:
        await collection.drop_index(legacy_unique_index)

    await collection.create_index(
        [("event_type", ASCENDING), ("event_id", ASCENDING), ("user_id", ASCENDING)],
        unique=True,
        name="event_type_1_event_id_1_user_id_1",
    )


async def init_db():
    await init_beanie(
        database=client[DB_NAME],
        document_models=[
            Attendance,
            AuditLog,
            User,
            Role,
            UserRole,
            UserUnit,
            Unit,
            Semester,
            RefreshTokenSession,
            PublicEvent,
            Report,
            EventRegistration,
            UnitEvent,
            UnitEventSubmission,
            UnitEventSubmissionMember,
            EventPromotion,
        ],
    )
    await _sync_attendance_indexes()


def get_db():
    return client[DB_NAME]
