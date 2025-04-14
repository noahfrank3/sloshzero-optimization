import asyncio
import os

from dask.distributed import Scheduler

async def start_scheduler():
    port = int(os.environ.get("PORT", 8786))
    scheduler = Scheduler(port=port)
    await scheduler.start()
    await asyncio.Event().wait()

asyncio.run(start_scheduler())
