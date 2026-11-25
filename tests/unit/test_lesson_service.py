from datetime import datetime, timezone
from unittest.mock import Mock
import pytest
from internal.domain.errors import ErrInvalidInput
from internal.domain.models import Lesson
from internal.service.lesson_service import LessonService

def test_create_lesson_success():
    repo = Mock()
    lesson = Lesson(subject_id="subject-1", group_id="group-1", teacher_id="teacher-1",
                    lesson_date=datetime(2026, 11, 16, 10, 0, tzinfo=timezone.utc), lesson_type="lecture")
    repo.create.return_value = lesson
    result = LessonService(repo).create(lesson)
    repo.create.assert_called_once_with(lesson)
    assert result.lesson_type == "lecture"

def test_create_lesson_rejects_unknown_type():
    repo = Mock()
    lesson = Lesson(subject_id="subject-1", group_id="group-1", teacher_id="teacher-1",
                    lesson_date=datetime.now(timezone.utc), lesson_type="party")
    with pytest.raises(ErrInvalidInput): LessonService(repo).create(lesson)
    repo.create.assert_not_called()
