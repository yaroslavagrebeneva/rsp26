from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from internal.domain.errors import ErrConflict, ErrInvalidInput
from internal.domain.models import QRSession
from internal.service.qr_session_service import QRSessionService

NOW = datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc)

def make_service(active=None):
    lessons = Mock()
    lessons.get_by_id.return_value = SimpleNamespace(lesson_id="lesson-1")
    sessions = Mock()
    sessions.find_active_by_lesson.return_value = active
    sessions.create.side_effect = lambda x: QRSession(qr_session_id="session-1", lesson_id=x.lesson_id,
        token=x.token, created_at=x.created_at, expires_at=x.expires_at, status=x.status)
    service = QRSessionService(lessons, sessions, clock=lambda: NOW, token_factory=lambda: "secret-token")
    return service, lessons, sessions

def test_create_qr_session_success():
    service, lessons, sessions = make_service()
    result = service.create("lesson-1", 5)
    lessons.get_by_id.assert_called_once_with("lesson-1")
    sessions.find_active_by_lesson.assert_called_once_with("lesson-1")
    sessions.create.assert_called_once()
    assert result.status == "active"
    assert result.expires_at == NOW + timedelta(minutes=5)

def test_create_rejected_when_active_session_exists():
    active = QRSession(qr_session_id="old", lesson_id="lesson-1", status="active")
    service, _, sessions = make_service(active)
    with pytest.raises(ErrConflict): service.create("lesson-1", 5)
    sessions.create.assert_not_called()

def test_create_rejects_ttl_outside_range():
    service, _, sessions = make_service()
    with pytest.raises(ErrInvalidInput): service.create("lesson-1", 30)
    sessions.create.assert_not_called()

def test_close_rejects_already_closed_session():
    service, _, sessions = make_service()
    sessions.get_by_id.return_value = QRSession(qr_session_id="s1", lesson_id="lesson-1", status="closed")
    with pytest.raises(ErrConflict): service.close("s1")
    sessions.update_status.assert_not_called()
