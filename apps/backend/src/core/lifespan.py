from contextlib import asynccontextmanager

from fastapi import FastAPI

startup_tasks = []
shutdown_tasks = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App lifespan context manager handling startup and shutdown tasks.
    """
    # Run registered startup tasks
    for task in startup_tasks:
        await task()

    yield

    # Run registered shutdown tasks
    for task in shutdown_tasks:
        await task()
