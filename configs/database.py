import os

from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from models.event_registration import EventRegistration
from models.public_event import PublicEvent
from models.report import Report
from models.roles import Role
from models.semester import Semester
from models.unit import Unit
from models.unit_event import UnitEvent
from models.users import User
from models.users_roles import UserRole

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)


async def init_db():
    await init_beanie(
        database=client[DB_NAME],
        document_models=[
            User,
            Role,
            UserRole,
            Unit,
            Semester,
            PublicEvent,
            Report,
            EventRegistration,
            UnitEvent,
        ],
    )


def get_db():
    return client[DB_NAME]
