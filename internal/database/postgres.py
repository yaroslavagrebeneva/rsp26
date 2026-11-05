"""Создание ограниченного пула PostgreSQL с повторными попытками подключения."""

import logging
import time
from typing import Optional

from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from internal.config.settings import Settings

logger = logging.getLogger(__name__)
MAX_ATTEMPTS = 10


def create_pool(settings: Settings) -> ConnectionPool:
    """Подключается к PostgreSQL; повторяет попытки, если БД ещё запускается."""
    pool: Optional[ConnectionPool] = None
    last_error: Optional[Exception] = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            pool = ConnectionPool(
                conninfo=settings.database_url,
                min_size=1,
                max_size=settings.db_max_conns,
                timeout=3,
                open=False,
                kwargs={"connect_timeout": 3, "row_factory": dict_row},
                name="checkin-postgres-pool",
            )
            pool.open(wait=True, timeout=4)
            with pool.connection(timeout=3) as connection:
                connection.execute("SELECT 1")
            logger.info(
                "PostgreSQL connection established (host=%s, port=%s, pool_max=%s)",
                settings.db_host,
                settings.db_port,
                settings.db_max_conns,
            )
            return pool
        except Exception as exc:  # ошибка старта должна привести к повторной попытке
            last_error = exc
            if pool is not None:
                pool.close()
                pool = None
            delay = min(attempt, 5)
            logger.warning(
                "PostgreSQL connection attempt %s/%s failed (%s); retry in %ss",
                attempt,
                MAX_ATTEMPTS,
                type(exc).__name__,
                delay,
            )
            if attempt < MAX_ATTEMPTS:
                time.sleep(delay)

    raise RuntimeError(
        f"Не удалось подключиться к PostgreSQL после {MAX_ATTEMPTS} попыток. "
        "Проверьте доступность сервиса db и значения DB_HOST/DB_PORT/DB_USER/DB_NAME."
    ) from last_error
