"""Преобразование доменных ошибок в HTTP-ответы на уровне контроллера."""
from fastapi import HTTPException
from internal.domain.errors import ErrNotFound, ErrAlreadyExists, ErrConflict, ErrInvalidInput


def to_http_exception(error: Exception) -> HTTPException:
    if isinstance(error, ErrNotFound):
        return HTTPException(status_code=404, detail=str(error))
    if isinstance(error, (ErrAlreadyExists, ErrConflict)):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, ErrInvalidInput):
        return HTTPException(status_code=400, detail=str(error))
    return HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
