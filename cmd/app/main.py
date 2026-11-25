"""Точка входа FastAPI и жизненный цикл пула PostgreSQL."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from internal.config.settings import settings
from internal.controller.health_controller import router as health_router
from internal.database.postgres import create_pool
from internal.repository.postgres import (
    PostgresUserRepository, PostgresSubjectRepository, PostgresAttendanceRepository,
)
from internal.repository.postgres.lesson_repository import PostgresLessonRepository
from internal.repository.postgres.qr_session_repository import PostgresQRSessionRepository
from internal.service.lesson_service import LessonService
from internal.service.qr_session_service import QRSessionService
from internal.controller.lesson_controller import router as lesson_router
from internal.controller.qr_session_controller import router as qr_session_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создание пула блокирует старт, пока БД не станет доступной.
    pool = create_pool(settings)
    app.state.db_pool = pool
    # Внедрение зависимостей: репозитории получают общий пул PostgreSQL.
    app.state.user_repository = PostgresUserRepository(pool)
    app.state.subject_repository = PostgresSubjectRepository(pool)
    app.state.attendance_repository = PostgresAttendanceRepository(pool)
    lesson_repository = PostgresLessonRepository(pool)
    qr_session_repository = PostgresQRSessionRepository(pool)
    app.state.lesson_repository = lesson_repository
    app.state.qr_session_repository = qr_session_repository
    app.state.lesson_service = LessonService(lesson_repository)
    app.state.qr_session_service = QRSessionService(lesson_repository, qr_session_repository)
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
app.include_router(lesson_router)
app.include_router(qr_session_router)


@app.get("/", tags=["System"])
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "message": "CheckIn Backend Service is running",
    }
