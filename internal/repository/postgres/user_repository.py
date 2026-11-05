from typing import List
"""PostgreSQL-реализация репозитория пользователей."""
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from internal.domain.models import User
from internal.domain.errors import ErrNotFound
from internal.repository.postgres.base import execute_safely, normalize_pagination

class PostgresUserRepository:
    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    @staticmethod
    def _model(row: dict) -> User:
        return User(**row)

    def create(self, user: User) -> User:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute(
                    """INSERT INTO users
                    (role_id, group_id, department_id, first_name, last_name, email, phone, password_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING user_id, role_id, group_id, department_id, first_name, last_name,
                              email, phone, password_hash, created_at""",
                    (user.role_id, user.group_id, user.department_id, user.first_name,
                     user.last_name, user.email, user.phone, user.password_hash),
                ).fetchone()
                return self._model(row)
        return execute_safely(operation)

    def get_by_id(self, user_id: str) -> User:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute(
                    """SELECT user_id, role_id, group_id, department_id, first_name, last_name,
                              email, phone, password_hash, created_at
                       FROM users WHERE user_id = %s""", (user_id,),
                ).fetchone()
                if row is None:
                    raise ErrNotFound("Пользователь не найден")
                return self._model(row)
        return execute_safely(operation)

    def get_by_email(self, email: str) -> User:
        def operation():
            with self.pool.connection() as conn:
                row = conn.execute(
                    """SELECT user_id, role_id, group_id, department_id, first_name, last_name,
                              email, phone, password_hash, created_at
                       FROM users WHERE email = %s""", (email,),
                ).fetchone()
                if row is None:
                    raise ErrNotFound("Пользователь с таким email не найден")
                return self._model(row)
        return execute_safely(operation)

    def list(self, limit: int = 20, offset: int = 0) -> List[User]:
        limit, offset = normalize_pagination(limit, offset)
        def operation():
            with self.pool.connection() as conn:
                rows = conn.execute(
                    """SELECT user_id, role_id, group_id, department_id, first_name, last_name,
                              email, phone, password_hash, created_at
                       FROM users ORDER BY created_at DESC, user_id LIMIT %s OFFSET %s""",
                    (limit, offset),
                ).fetchall()
                return [self._model(row) for row in rows]
        return execute_safely(operation)

    def delete(self, user_id: str) -> None:
        def operation():
            with self.pool.connection() as conn:
                cur = conn.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                if cur.rowcount == 0:
                    raise ErrNotFound("Пользователь не найден")
        return execute_safely(operation)
