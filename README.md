<div align="left">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExODNiZDFvOHBhc3EyZWJveHg2a3d6ZTZrbXV4cTgyMWk1dGVpNWsxdyZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/MelhioWPAo6k4Q6BTp/giphy.gif" width="60"/>
</div>

# Лабораторная работа №7 — CheckIn

## Реализованные сущности
- Первая сущность: `lessons` — полный CRUD: POST, GET по ID, GET со страницами `limit`/`offset`, PUT, DELETE.
- Вторая сущность: `qr_sessions` — создание, чтение по ID, список сессий занятия и завершение (смена состояния `active` → `closed`). Связь обеспечивается `lesson_id`.

## Бизнес-правила QR-сессий
1. QR-сессия создаётся только для существующего занятия.
2. Срок действия QR-сессии составляет от 1 до 15 минут.
3. Для одного занятия не допускается создание второй одновременно активной и неистёкшей QR-сессии.
4. Завершить можно только QR-сессию в состоянии `active`.

## Архитектура
HTTP-контроллеры принимают и возвращают DTO и вызывают сервисы. Сервисы получают репозитории через внедрение зависимостей; QRSessionService дополнительно получает часы и генератор токена. SQL находится только в PostgreSQL-репозиториях. Доменные ошибки преобразуются в HTTP-коды централизованно в `internal/controller/error_mapping.py`.

## DTO и конфиденциальность
Для запросов и ответов определены отдельные Pydantic DTO. Публичный `QRSessionResponseDTO` не содержит внутренний токен QR-сессии. Пароль пользователя не включается в публичный DTO пользователя (см. `User.to_public_dict`).

## Миграция
Добавлена миграция `000002_qr_session_status.up.sql`; она добавляет `status`, `closed_at`, CHECK-ограничение и индекс. Откат находится в `000002_qr_session_status.down.sql`.

## Запуск
Из WSL:
```bash
cd /mnt/d/serverrazrabotka
sudo service docker start
sudo docker compose up --build -d
sudo docker compose ps
curl http://localhost:8080/api/v1/health
```
