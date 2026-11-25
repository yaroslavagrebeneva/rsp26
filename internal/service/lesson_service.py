"""Сервис бизнес-операций над занятиями."""
from internal.domain.models import Lesson
from internal.domain.errors import ErrInvalidInput

ALLOWED_LESSON_TYPES = {"lecture", "practice", "laboratory", "seminar", "other"}

class LessonService:
    def __init__(self, repository): self.repository = repository
    def create(self, lesson: Lesson) -> Lesson:
        self._validate(lesson)
        return self.repository.create(lesson)
    def get(self, lesson_id: str) -> Lesson: return self.repository.get_by_id(lesson_id)
    def list(self, limit: int, offset: int): return self.repository.list(limit, offset)
    def update(self, lesson: Lesson) -> Lesson:
        self._validate(lesson)
        if not lesson.lesson_id: raise ErrInvalidInput("Не указан идентификатор занятия")
        return self.repository.update(lesson)
    def delete(self, lesson_id: str) -> None: self.repository.delete(lesson_id)
    @staticmethod
    def _validate(item):
        if not item.subject_id or not item.group_id or not item.teacher_id or not item.lesson_date:
            raise ErrInvalidInput("Для занятия обязательны предмет, группа, преподаватель и дата")
        if item.lesson_type not in ALLOWED_LESSON_TYPES:
            raise ErrInvalidInput("Недопустимый тип занятия")
