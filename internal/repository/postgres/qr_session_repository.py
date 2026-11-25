"""PostgreSQL-репозиторий QR-сессий."""
from psycopg_pool import ConnectionPool
from internal.domain.models import QRSession
from internal.domain.errors import ErrNotFound
from internal.repository.postgres.base import execute_safely

class PostgresQRSessionRepository:
    def __init__(self, pool: ConnectionPool): self.pool = pool
    @staticmethod
    def _model(row): return QRSession(**row)

    def create(self, item: QRSession) -> QRSession:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute("""INSERT INTO qr_sessions (lesson_id, token, expires_at, status)
                    VALUES (%s, %s, %s, 'active')
                    RETURNING qr_session_id, lesson_id, token, created_at, expires_at, status, closed_at""",
                    (item.lesson_id, item.token, item.expires_at)).fetchone()
                return self._model(row)
        return execute_safely(operation)

    def get_by_id(self, session_id: str) -> QRSession:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute("""SELECT qr_session_id, lesson_id, token, created_at, expires_at, status, closed_at
                    FROM qr_sessions WHERE qr_session_id=%s""", (session_id,)).fetchone()
                if row is None: raise ErrNotFound("QR-сессия не найдена")
                return self._model(row)
        return execute_safely(operation)

    def list_by_lesson(self, lesson_id: str):
        def operation():
            with self.pool.connection() as conn:
                rows = conn.execute("""SELECT qr_session_id, lesson_id, token, created_at, expires_at, status, closed_at
                    FROM qr_sessions WHERE lesson_id=%s ORDER BY created_at DESC, qr_session_id""", (lesson_id,)).fetchall()
                return [self._model(row) for row in rows]
        return execute_safely(operation)

    def find_active_by_lesson(self, lesson_id: str):
        def operation():
            with self.pool.connection() as conn:
                # Истёкшие записи выводятся из active; частичный уникальный индекс
                # не допускает две активные сессии даже при конкурентных запросах.
                conn.execute("UPDATE qr_sessions SET status='expired' WHERE lesson_id=%s AND status='active' AND expires_at <= now()", (lesson_id,))
                row = conn.execute("""SELECT qr_session_id, lesson_id, token, created_at, expires_at, status, closed_at
                    FROM qr_sessions WHERE lesson_id=%s AND status='active' AND expires_at > now()
                    ORDER BY created_at DESC LIMIT 1""", (lesson_id,)).fetchone()
                return self._model(row) if row else None
        return execute_safely(operation)

    def update_status(self, session_id: str, status: str, closed_at):
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute("""UPDATE qr_sessions SET status=%s, closed_at=%s
                    WHERE qr_session_id=%s AND status='active'
                    RETURNING qr_session_id, lesson_id, token, created_at, expires_at, status, closed_at""",
                    (status, closed_at, session_id)).fetchone()
                if row is None: raise ErrNotFound("Активная QR-сессия не найдена")
                return self._model(row)
        return execute_safely(operation)
