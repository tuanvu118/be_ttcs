from fastapi import FastAPI

from configs.cloudinary import init_cloudinary
from configs.database import init_db
from configs.seed_roles import seed_roles
from routers.auth import router as auth_router
from routers.event_registration import router as event_registration_router
from routers.public_event import router as public_event_router
from routers.rbac import router as rbac_router
from routers.report import router as report_router
from routers.semester import router as semester_router
from routers.unit import router as unit_router
from routers.unit_event import router as unit_event_router
from routers.users import router as users_router

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()
    init_cloudinary()
    await seed_roles()


app.include_router(auth_router)
app.include_router(rbac_router)
app.include_router(users_router)
app.include_router(unit_router)
app.include_router(semester_router)
app.include_router(public_event_router)
app.include_router(report_router)
app.include_router(event_registration_router)
app.include_router(unit_event_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to My FastAPI Application!"}
