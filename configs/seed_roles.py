from passlib.context import CryptContext

from models.roles import Role, RoleCode
from models.users import User
from models.users_roles import UserRole
from models.don_vi import DonVi


DEFAULT_ROLES = [RoleCode.ADMIN, RoleCode.MANAGER, RoleCode.STAFF, RoleCode.USER]


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


async def seed_roles():
    # Seed bảng roles
    for code in DEFAULT_ROLES:
        exists = await Role.find_one(Role.code == code)
        if not exists:
            await Role(code=code).insert()

    # Seed tài khoản ADMIN mặc định (ma_sv = ADMIN, password = ADMIN)
    admin_user = await User.find_one(User.ma_sv == "ADMIN")
    if not admin_user:
        hashed_password = pwd_context.hash("ADMIN")

        admin_user = User(
            ho_ten="Administrator",
            email="admin@example.com",
            password_hash=hashed_password,
            ma_sv="ADMIN",
            lop="ADMIN",
            khoa="SYSTEM",
            avatar=None,
            ngay_sinh=None,
        )
        admin_user = await admin_user.insert()

    # Đảm bảo có đơn vị mặc định để gán role ADMIN
    default_don_vi = await DonVi.find_one(DonVi.ten == "DEFAULT")
    if not default_don_vi:
        default_don_vi = DonVi(
            ten="DEFAULT",
            logo=None,
            loai="SYSTEM",
        )
        default_don_vi = await default_don_vi.insert()

    # Gán role ADMIN cho tài khoản ADMIN ở đơn vị DEFAULT nếu chưa có
    admin_role = await Role.find_one(Role.code == RoleCode.ADMIN)

    if admin_role:
        exists_user_role = await UserRole.find_one(
            (UserRole.user_id == admin_user.id),
             (UserRole.role_id == admin_role.id),
            (UserRole.don_vi_id == default_don_vi.id),
             (UserRole.is_active == True),
        )

        if not exists_user_role:
            await UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id,
                don_vi_id=default_don_vi.id,
                is_active=True,
            ).insert()
