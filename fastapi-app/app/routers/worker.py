from fastapi import APIRouter, BackgroundTasks
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

router = APIRouter(prefix="/worker", tags=["worker"])


executor = ThreadPoolExecutor(max_workers=5)


def blocking_task(n: int):
    time.sleep(n)
    return f"Task {n} done"


@router.get("/slow-task")
async def run_slow_task(n: int):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, blocking_task, n)
    return {"message": result}


@router.get("/background-task")
async def run_background_task(n: int, background_tasks: BackgroundTasks):
    """Run a blocking task in the background."""
    background_tasks.add_task(blocking_task, n)
    return {"message": "Task started!"}
