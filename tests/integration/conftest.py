import os
import pytest
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

@pytest.fixture(scope="session")
def test_pool():
    dsn = os.getenv("TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("TEST_DATABASE_URL не задан; тесты требуют отдельную БД с миграцией ЛР №5")
    pool = ConnectionPool(conninfo=dsn, min_size=1, max_size=5,
                          kwargs={"row_factory": dict_row}, open=True)
    with pool.connection() as conn:
        conn.execute("SELECT 1")
    yield pool
    pool.close()
