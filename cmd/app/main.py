"""Точка входа FastAPI и жизненный цикл пула PostgreSQL."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from internal.config.settings import settings
from internal.controller.health_controller import router as health_router
from internal.database.postgres import create_pool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создание пула блокирует старт, пока БД не станет доступной.
    pool = create_pool(settings)
    app.state.db_pool = pool
    try:
        yield
    finally:
        pool.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend service веб-системы CheckIn для учета посещаемости студентов.",
    lifespan=lifespan,
)
app.include_router(health_router)


@app.get("/", tags=["System"])
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "message": "CheckIn Backend Service is running",
    }
