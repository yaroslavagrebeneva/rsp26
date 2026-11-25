"""PostgreSQL-репозиторий занятий."""
from psycopg_pool import ConnectionPool
from internal.domain.models import Lesson
from internal.domain.errors import ErrNotFound
from internal.repository.postgres.base import execute_safely, normalize_pagination

class PostgresLessonRepository:
    def __init__(self, pool: ConnectionPool): self.pool = pool

    @staticmethod
    def _model(row): return Lesson(**row)

    def create(self, item: Lesson) -> Lesson:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute("""INSERT INTO lessons
                    (subject_id, group_id, teacher_id, lesson_date, lesson_type)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING lesson_id, subject_id, group_id, teacher_id, lesson_date, lesson_type, created_at""",
                    (item.subject_id, item.group_id, item.teacher_id, item.lesson_date, item.lesson_type)).fetchone()
                return self._model(row)
        return execute_safely(operation)

    def get_by_id(self, lesson_id: str) -> Lesson:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute("""SELECT lesson_id, subject_id, group_id, teacher_id, lesson_date, lesson_type, created_at
                    FROM lessons WHERE lesson_id = %s""", (lesson_id,)).fetchone()
                if row is None: raise ErrNotFound("Занятие не найдено")
                return self._model(row)
        return execute_safely(operation)

    def list(self, limit: int = 20, offset: int = 0):
        limit, offset = normalize_pagination(limit, offset)
        def operation():
            with self.pool.connection() as conn:
                rows = conn.execute("""SELECT lesson_id, subject_id, group_id, teacher_id, lesson_date, lesson_type, created_at
                    FROM lessons ORDER BY lesson_date DESC, lesson_id LIMIT %s OFFSET %s""", (limit, offset)).fetchall()
                return [self._model(row) for row in rows]
        return execute_safely(operation)

    def update(self, item: Lesson) -> Lesson:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute("""UPDATE lessons SET subject_id=%s, group_id=%s, teacher_id=%s,
                    lesson_date=%s, lesson_type=%s WHERE lesson_id=%s
                    RETURNING lesson_id, subject_id, group_id, teacher_id, lesson_date, lesson_type, created_at""",
                    (item.subject_id, item.group_id, item.teacher_id, item.lesson_date, item.lesson_type, item.lesson_id)).fetchone()
                if row is None: raise ErrNotFound("Занятие не найдено")
                return self._model(row)
        return execute_safely(operation)

    def delete(self, lesson_id: str) -> None:
        def operation():
            with self.pool.connection() as conn:
                cur = conn.execute("DELETE FROM lessons WHERE lesson_id=%s", (lesson_id,))
                if cur.rowcount == 0: raise ErrNotFound("Занятие не найдено")
        return execute_safely(operation)
