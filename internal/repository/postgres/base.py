
"""Общие функции PostgreSQL-репозиториев на psycopg 3."""

from internal.domain.errors import (
    ErrNotFound,
    ErrAlreadyExists,
    ErrConflict,
    ErrInvalidInput,
)
from typing import Tuple


def map_database_error(exc: Exception) -> Exception:
    """Преобразует SQLSTATE PostgreSQL в независимые доменные ошибки."""
    code = getattr(exc, "sqlstate", None)

    if code == "23505":
        return ErrAlreadyExists(
            "Запись с таким уникальным значением уже существует"
        )

    if code == "23503":
        return ErrConflict(
            "Операция нарушает связь с другой записью"
        )

    if code in ("23514", "22P02", "22001", "23502"):
        return ErrInvalidInput(
            "Данные не прошли проверку PostgreSQL"
        )

    return exc


def execute_safely(operation):
    """Выполняет операцию и переводит известные ошибки БД в доменные."""
    try:
        return operation()
    except Exception as exc:
        mapped = map_database_error(exc)

        if mapped is exc:
            raise

        raise mapped from exc


def normalize_pagination(limit: int, offset: int) -> Tuple[int, int]:
    """Ограничивает размер страницы и не допускает отрицательное смещение."""
    safe_limit = 20 if limit <= 0 else min(limit, 100)
    safe_offset = max(offset, 0)

    return safe_limit, safe_offset
