from datetime import datetime, timezone

from passlib.context import CryptContext

from models.roles import Role, RoleCode
from models.semester import Semester
from models.unit import Unit
from models.users import User
from models.users_roles import UserRole


DEFAULT_ROLES = [RoleCode.ADMIN, RoleCode.MANAGER, RoleCode.STAFF, RoleCode.USER]


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

DEFAULT_SEMESTER_NAME = "Hoc ky 2"
DEFAULT_SEMESTER_ACADEMIC_YEAR = "2025-2026"
DEFAULT_SEMESTER_START = datetime(2026, 2, 1, tzinfo=timezone.utc)
DEFAULT_SEMESTER_END = datetime(2026, 8, 31, 23, 59, 59, tzinfo=timezone.utc)


async def seed_roles():
    for code in DEFAULT_ROLES:
        exists = await Role.find_one(Role.code == code)
        if not exists:
            await Role(code=code).insert()

    admin_user = await User.find_one(User.student_id == "ADMIN")
    if not admin_user:
        hashed_password = pwd_context.hash("ADMIN")

        admin_user = User(
            full_name="Administrator",
            email="admin@example.com",
            password_hash=hashed_password,
            student_id="ADMIN",
            class_name="ADMIN",
            avatar_url=None,
            date_of_birth=None,
        )
        admin_user = await admin_user.insert()

    default_unit = await Unit.find_one(Unit.name == "DEFAULT")
    if not default_unit:
        default_unit = Unit(
            name="DEFAULT",
            logo=None,
            type="SYSTEM",
        )
        default_unit = await default_unit.insert()

    seeded_semester = await Semester.find_one(
        Semester.name == DEFAULT_SEMESTER_NAME,
        Semester.academic_year == DEFAULT_SEMESTER_ACADEMIC_YEAR,
    )
    if not seeded_semester:
        seeded_semester = Semester(
            name=DEFAULT_SEMESTER_NAME,
            academic_year=DEFAULT_SEMESTER_ACADEMIC_YEAR,
            start_date=DEFAULT_SEMESTER_START,
            end_date=DEFAULT_SEMESTER_END,
            is_active=True,
        )
        seeded_semester = await seeded_semester.insert()
    elif not seeded_semester.is_active:
        seeded_semester.is_active = True
        seeded_semester.start_date = DEFAULT_SEMESTER_START
        seeded_semester.end_date = DEFAULT_SEMESTER_END
        await seeded_semester.save()

    other_active_semesters = await Semester.find(
        Semester.is_active == True,
        Semester.id != seeded_semester.id,
    ).to_list()
    for semester in other_active_semesters:
        semester.is_active = False
        await semester.save()

    admin_role = await Role.find_one(Role.code == RoleCode.ADMIN)
    if admin_role:
        exists_user_role = await UserRole.find_one(
            (UserRole.user_id == admin_user.id),
            (UserRole.role_id == admin_role.id),
            (UserRole.unit_id == default_unit.id),
            (UserRole.semester_id == seeded_semester.id),
            (UserRole.is_active == True),
        )

        if not exists_user_role:
            await UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id,
                unit_id=default_unit.id,
                semester_id=seeded_semester.id,
                is_active=True,
            ).insert()
