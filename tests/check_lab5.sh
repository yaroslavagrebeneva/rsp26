#!/usr/bin/env bash
# Ручной smoke-test лабораторной № 5. Запускать из корня проекта в WSL/Ubuntu.
set -euo pipefail

DB_USER="$(grep '^DB_USER=' .env | cut -d= -f2-)"
DB_NAME="$(grep '^DB_NAME=' .env | cut -d= -f2-)"
DB_PASSWORD="$(grep '^DB_PASSWORD=' .env | cut -d= -f2-)"

printf '\n[1/5] Состояние контейнеров\n'
docker compose ps -a
printf '\n[2/5] Таблицы\n'
docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c '\dt'
printf '\n[3/5] Версия миграции\n'
docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c 'SELECT version, dirty FROM schema_migrations;'
printf '\n[4/5] Проверка health endpoint (ожидается HTTP 200)\n'
curl -i http://localhost:"$(grep '^HTTP_PORT=' .env | cut -d= -f2-)"/health
printf '\n[5/5] Проверка ограничения CHECK\n'
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" -c "INSERT INTO roles(name) VALUES ('test-role');"
if docker compose exec -T db psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" -c "INSERT INTO roles(name) VALUES ('   ');"; then
  echo 'ОШИБКА: ограничение CHECK не сработало'
  exit 1
else
  echo 'Ожидаемый результат: PostgreSQL отклонил некорректное значение по CHECK'
fi
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" -c "DELETE FROM roles WHERE name = 'test-role';"
printf '\nБазовые проверки завершены. Откат, 503 и сохранность тома выполняются командами из README_LAB5.md.\n'
