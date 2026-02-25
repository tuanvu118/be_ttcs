import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from models.users import User
from models.roles import Role
from models.users_roles import UserRole
from models.don_vi import DonVi
from models.public_event import PublicEvent
from models.report import Report
from models.event_registration import EventRegistration

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)

async def init_db():
    await init_beanie(
        database=client[DB_NAME],
        document_models=[User, Role, UserRole, DonVi, PublicEvent,Report,EventRegistration],
    )

def get_db():
    return client[DB_NAME]

