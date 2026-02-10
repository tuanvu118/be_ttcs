from fastapi import FastAPI

from configs.cloudinary import init_cloudinary
from configs.database import init_db  # tuỳ bạn đặt
from configs.seed_roles import seed_roles
from routers.auth import router as auth_router
from routers.rbac import router as rbac_router
from routers.users import router as users_router
from routers.don_vi import router as donvi_router

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()
    init_cloudinary()
    await seed_roles()  # chỉ chạy khi database trống       


app.include_router(auth_router)
app.include_router(rbac_router)
app.include_router(users_router)
app.include_router(donvi_router)


@app.get("/")  # 127.0.0.1:8000/
def read_root():
    return {"message": "Welcome to My FastAPI Application!"}

