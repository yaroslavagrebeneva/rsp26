from typing import List
"""PostgreSQL-реализация репозитория учебных предметов."""
from psycopg_pool import ConnectionPool
from internal.domain.models import Subject
from internal.domain.errors import ErrNotFound
from internal.repository.postgres.base import execute_safely, normalize_pagination

class PostgresSubjectRepository:
    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    @staticmethod
    def _model(row: dict) -> Subject:
        return Subject(**row)

    def create(self, subject: Subject) -> Subject:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute(
                    "INSERT INTO subjects (name) VALUES (%s) RETURNING subject_id, name",
                    (subject.name,),
                ).fetchone()
                return self._model(row)
        return execute_safely(operation)

    def get_by_id(self, subject_id: str) -> Subject:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute(
                    "SELECT subject_id, name FROM subjects WHERE subject_id = %s", (subject_id,),
                ).fetchone()
                if row is None:
                    raise ErrNotFound("Учебный предмет не найден")
                return self._model(row)
        return execute_safely(operation)

    def list(self, limit: int = 20, offset: int = 0) -> List[Subject]:
        limit, offset = normalize_pagination(limit, offset)
        def operation():
            with self.pool.connection() as conn:
                rows = conn.execute(
                    "SELECT subject_id, name FROM subjects ORDER BY name, subject_id LIMIT %s OFFSET %s",
                    (limit, offset),
                ).fetchall()
                return [self._model(row) for row in rows]
        return execute_safely(operation)

    def update(self, subject: Subject) -> None:
        def operation():
            with self.pool.connection() as conn:
                cur = conn.execute(
                    "UPDATE subjects SET name = %s WHERE subject_id = %s",
                    (subject.name, subject.subject_id),
                )
                if cur.rowcount == 0:
                    raise ErrNotFound("Учебный предмет не найден")
        return execute_safely(operation)

    def delete(self, subject_id: str) -> None:
        def operation():
            with self.pool.connection() as conn:
                cur = conn.execute("DELETE FROM subjects WHERE subject_id = %s", (subject_id,))
                if cur.rowcount == 0:
                    raise ErrNotFound("Учебный предмет не найден")
        return execute_safely(operation)
