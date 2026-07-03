from contextlib import asynccontextmanager

from fastapi import FastAPI

startup_tasks = []
shutdown_tasks = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.shared.infrastructure.geoip.geoip_service import geoip_service

    # Load the MaxMind GeoLite2 reader once; lookups are then in-memory.
    geoip_service.load()

    for task in startup_tasks:
        await task()

    yield

    for task in shutdown_tasks:
        await task()

    geoip_service.close()
