# Лабораторная работа № 5 — CheckIn + PostgreSQL + Docker Compose

## Что добавлено

- PostgreSQL 16 в сервисе `db`, именованный том `pgdata` и `healthcheck` через `pg_isready`.
- Сервис `migrate` на `golang-migrate`, который применяет SQL-миграции до запуска приложения.
- Сервис `app`, собранный из существующего `Dockerfile`.
- `migrations/000001_init_schema.up.sql` и `migrations/000001_init_schema.down.sql`. Миграция создаёт 16 таблиц предметной области CheckIn, ограничения PK/FK/NOT NULL/UNIQUE/CHECK и индексы для внешних ключей.
- `internal/config/settings.py`: загрузка и валидация `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_MAX_CONNS`.
- `internal/database/postgres.py`: ограниченный пул `psycopg_pool`, проверка соединения и повторные попытки старта.
- `/health` и `/api/v1/health`: HTTP 200 при доступной БД и HTTP 503 при недоступной БД.
- `.env.example`; настоящий `.env` исключён из Git через `.gitignore`.


```bash
# Если Docker Engine не запущен в WSL:
sudo service docker start

# Проверить Docker и Compose
docker --version
docker compose version
docker run --rm hello-world

# Перейти в корень проекта (замените путь на свой)
cd ~/serverrazrabotka

# Собрать приложение и запустить сервисы
docker compose up --build -d

# Посмотреть состояние контейнеров
docker compose ps -a
```

Ожидаемо: `db` — `Up ... (healthy)`, `migrate` — `Exited (0)`, `app` — `Up`. 
## Проверка задания

```bash
# Журналы миграции и приложения
docker compose logs migrate
docker compose logs app

# Список таблиц и версия применённой миграции
# Логин и имя БД берутся из .env
grep '^DB_USER=' .env
grep '^DB_NAME=' .env
docker compose exec db psql -U checkin_user -d checkin_db -c '\dt'
docker compose exec db psql -U checkin_user -d checkin_db -c 'SELECT version, dirty FROM schema_migrations;'

# Проверка API (должен быть HTTP 200 и db=up)
curl -i http://localhost:8080/health
curl -i http://localhost:8080/api/v1/health


```

Если изменяли `DB_USER`, `DB_NAME` или `HTTP_PORT`, замените значения в командах или используйте значения из `.env`.

## Проверка ответа 503

В одном терминале остановите БД:

```bash
docker compose stop db
```

В другом терминале проверьте endpoint:

```bash
curl -i http://localhost:8080/health
```

Ожидается `HTTP/1.1 503 Service Unavailable` и JSON `{"status":"unavailable","db":"down"}`. Затем восстановите БД:

```bash
docker compose start db
docker compose ps -a
curl -i http://localhost:8080/health
```

Пул в приложении проверяет соединение при запросе, поэтому `/health` показывает недоступность БД. После её возврата приложение продолжает использовать пул.

## Проверка сохранности данных после перезапуска

```bash
# Создать контрольную запись
# Значение роли должно быть уникальным
docker compose exec db psql -U checkin_user -d checkin_db -c "INSERT INTO roles(name) VALUES ('persistence_test');"

# Удалить контейнеры, не удаляя именованный том
docker compose down
docker compose up -d

# Запись должна сохраниться
docker compose exec db psql -U checkin_user -d checkin_db -c "SELECT name FROM roles WHERE name='persistence_test';"

# Удалить контрольную запись после проверки
docker compose exec db psql -U checkin_user -d checkin_db -c "DELETE FROM roles WHERE name='persistence_test';"
```

**Не используйте `docker compose down -v`, если хотите сохранить данные.** Флаг `-v` удаляет именованные тома.

## Откат и повторное применение миграции

Откат начальной миграции удаляет созданные ею таблицы и данные в них. Выполняйте его на учебной базе, а не на базе с нужными данными.

```bash
# Для значений из предоставленного .env:
docker compose run --rm --entrypoint migrate migrate \
  -path=/migrations \
  -database 'postgres://checkin_user:CheckIn2026Pass@db:5432/checkin_db?sslmode=disable' \
  down 1

# После отката пользовательских таблиц быть не должно (остаётся schema_migrations)
docker compose exec db psql -U checkin_user -d checkin_db -c '\dt'

# Повторное применение
docker compose run --rm --entrypoint migrate migrate \
  -path=/migrations \
  -database 'postgres://checkin_user:CheckIn2026Pass@db:5432/checkin_db?sslmode=disable' \
  up

docker compose exec db psql -U checkin_user -d checkin_db -c 'SELECT version, dirty FROM schema_migrations;'
```

Если изменили пользователя, пароль или имя БД в `.env`, замените их и в строке подключения для команд `down` и `up`. После `down 1` не запускайте `app`, пока не выполните повторный `up`: приложение ожидает актуальную схему.

## Очистка

```bash
# Остановить контейнеры, сохранив БД
docker compose down

# Полный сброс учебной БД (удалит данные без возможности восстановления)
# docker compose down -v
```
