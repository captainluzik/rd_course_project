from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
import asyncio
from concurrent.futures import ProcessPoolExecutor
from .update_load import update_load

jobstores = {
    'default': MemoryJobStore()
}

scheduler = AsyncIOScheduler(jobstores=jobstores)
executor = ProcessPoolExecutor()


async def run_update_load():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, update_load)


@scheduler.scheduled_job('interval', seconds=120)
async def job():
    await run_update_load()
    print("Job executed")
