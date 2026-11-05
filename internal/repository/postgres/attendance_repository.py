from typing import List
"""PostgreSQL-реализация репозитория отметок посещаемости."""
from psycopg_pool import ConnectionPool
from internal.domain.models import Attendance
from internal.domain.errors import ErrNotFound
from internal.repository.postgres.base import execute_safely, normalize_pagination

class PostgresAttendanceRepository:
    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    @staticmethod
    def _model(row: dict) -> Attendance:
        return Attendance(**row)

    def create(self, item: Attendance) -> Attendance:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute(
                    """INSERT INTO attendance
                       (lesson_id, student_id, qr_session_id, marked_by, status, method)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       RETURNING attendance_id, lesson_id, student_id, qr_session_id,
                                 marked_by, status, method, marked_at""",
                    (item.lesson_id, item.student_id, item.qr_session_id, item.marked_by,
                     item.status, item.method),
                ).fetchone()
                return self._model(row)
        return execute_safely(operation)

    def get_by_id(self, attendance_id: str) -> Attendance:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute(
                    """SELECT attendance_id, lesson_id, student_id, qr_session_id,
                              marked_by, status, method, marked_at
                       FROM attendance WHERE attendance_id = %s""", (attendance_id,),
                ).fetchone()
                if row is None:
                    raise ErrNotFound("Запись посещаемости не найдена")
                return self._model(row)
        return execute_safely(operation)

    def list(self, limit: int = 20, offset: int = 0) -> List[Attendance]:
        limit, offset = normalize_pagination(limit, offset)
        def operation():
            with self.pool.connection() as conn:
                rows = conn.execute(
                    """SELECT attendance_id, lesson_id, student_id, qr_session_id,
                              marked_by, status, method, marked_at
                       FROM attendance ORDER BY marked_at DESC, attendance_id LIMIT %s OFFSET %s""",
                    (limit, offset),
                ).fetchall()
                return [self._model(row) for row in rows]
        return execute_safely(operation)

    def update(self, item: Attendance) -> None:
        def operation():
            with self.pool.connection() as conn:
                cur = conn.execute(
                    """UPDATE attendance SET status = %s, method = %s, qr_session_id = %s,
                              marked_by = %s WHERE attendance_id = %s""",
                    (item.status, item.method, item.qr_session_id, item.marked_by, item.attendance_id),
                )
                if cur.rowcount == 0:
                    raise ErrNotFound("Запись посещаемости не найдена")
        return execute_safely(operation)

    def delete(self, attendance_id: str) -> None:
        def operation():
            with self.pool.connection() as conn:
                cur = conn.execute("DELETE FROM attendance WHERE attendance_id = %s", (attendance_id,))
                if cur.rowcount == 0:
                    raise ErrNotFound("Запись посещаемости не найдена")
        return execute_safely(operation)
