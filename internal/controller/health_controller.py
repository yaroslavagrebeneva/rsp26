"""Эндпоинты проверки состояния приложения и PostgreSQL."""

from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from internal.config.settings import settings

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)
START_TIME = datetime.now(timezone.utc)


@router.get("/health", summary="Проверка состояния сервера и базы данных")
@router.get("/api/v1/health", summary="Проверка состояния сервера и базы данных", include_in_schema=False)
def health_check(request: Request):
    """Возвращает 200 только при доступной БД; иначе возвращает 503."""
    pool = getattr(request.app.state, "db_pool", None)
    if pool is None:
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "db": "down"},
        )

    try:
        with pool.connection(timeout=2) as connection:
            connection.execute("SELECT 1")
    except Exception as exc:
        logger.warning("Health check failed: PostgreSQL is unavailable (%s)", type(exc).__name__)
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "db": "down"},
        )

    uptime = int((datetime.now(timezone.utc) - START_TIME).total_seconds())
    return {
        "status": "ok",
        "db": "up",
        "name": settings.app_name,
        "version": settings.app_version,
        "uptime": uptime,
    }
