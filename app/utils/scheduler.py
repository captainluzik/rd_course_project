from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
import asyncio
from .update_load import update_load

jobstores = {
    'default': MemoryJobStore()
}

scheduler = AsyncIOScheduler(jobstores=jobstores)


@scheduler.scheduled_job('interval', seconds=3600)
async def job():
    asyncio.create_task(update_load())
    print("Job executed")
