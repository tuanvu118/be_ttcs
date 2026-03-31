from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.report import ReportService

scheduler = AsyncIOScheduler()

scheduler.add_job(
    ReportService.auto_create_monthly_reports,
    "cron",
    day=1,
    hour=0,
    minute=0,
)