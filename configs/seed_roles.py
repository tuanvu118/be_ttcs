from passlib.context import CryptContext

from models.roles import Role, RoleCode
from models.semester import Semester
from models.unit import Unit
from models.users import User
from models.users_roles import UserRole


DEFAULT_ROLES = [RoleCode.ADMIN, RoleCode.MANAGER, RoleCode.STAFF, RoleCode.USER]


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


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

    admin_role = await Role.find_one(Role.code == RoleCode.ADMIN)
    active_semester = await Semester.find_one(Semester.is_active == True)

    if admin_role and active_semester:
        exists_user_role = await UserRole.find_one(
            (UserRole.user_id == admin_user.id),
            (UserRole.role_id == admin_role.id),
            (UserRole.unit_id == default_unit.id),
            (UserRole.semester_id == active_semester.id),
            (UserRole.is_active == True),
        )

        if not exists_user_role:
            await UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id,
                unit_id=default_unit.id,
                semester_id=active_semester.id,
                is_active=True,
            ).insert()
