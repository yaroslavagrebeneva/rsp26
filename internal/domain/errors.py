"""Общие доменные ошибки CheckIn."""

class DomainError(Exception):
    """Базовая ошибка предметной области."""

class ErrNotFound(DomainError):
    """Запрошенная запись не найдена."""

class ErrAlreadyExists(DomainError):
    """Нарушено ограничение уникальности."""

class ErrConflict(DomainError):
    """Операция конфликтует с существующими связями."""

class ErrInvalidInput(DomainError):
    """Переданы некорректные данные."""
