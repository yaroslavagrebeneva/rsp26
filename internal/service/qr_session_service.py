"""Бизнес-правила жизненного цикла QR-сессии."""
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from internal.domain.models import QRSession
from internal.domain.errors import ErrConflict, ErrInvalidInput

class QRSessionService:
    MIN_TTL_MINUTES = 1
    MAX_TTL_MINUTES = 15

    def __init__(self, lesson_repository, session_repository, clock=None, token_factory=None):
        self.lesson_repository = lesson_repository
        self.session_repository = session_repository
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.token_factory = token_factory or (lambda: token_urlsafe(32))

    def create(self, lesson_id: str, ttl_minutes: int = 5) -> QRSession:
        # Правило 1: QR-сессию можно создать только для существующего занятия.
        self.lesson_repository.get_by_id(lesson_id)
        # Правило 2: срок действия ограничен диапазоном от 1 до 15 минут.
        if ttl_minutes < self.MIN_TTL_MINUTES or ttl_minutes > self.MAX_TTL_MINUTES:
            raise ErrInvalidInput("Срок действия QR-сессии должен быть от 1 до 15 минут")
        # Правило 3: у занятия может быть только одна действующая QR-сессия.
        active = self.session_repository.find_active_by_lesson(lesson_id)
        if active is not None:
            raise ErrConflict("Для этого занятия уже существует активная QR-сессия")
        now = self.clock()
        session = QRSession(lesson_id=lesson_id, token=self.token_factory(),
                            created_at=now, expires_at=now + timedelta(minutes=ttl_minutes), status="active")
        return self.session_repository.create(session)

    def get(self, session_id: str) -> QRSession:
        return self.session_repository.get_by_id(session_id)

    def list_for_lesson(self, lesson_id: str):
        self.lesson_repository.get_by_id(lesson_id)
        return self.session_repository.list_by_lesson(lesson_id)

    def close(self, session_id: str) -> QRSession:
        session = self.session_repository.get_by_id(session_id)
        if session.status != "active":
            raise ErrConflict("Завершить можно только активную QR-сессию")
        return self.session_repository.update_status(session_id, "closed", self.clock())
