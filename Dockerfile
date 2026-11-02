
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

FROM python:${PYTHON_VERSION}-slim AS runtime

LABEL org.opencontainers.image.title="checkin-backend" \
      org.opencontainers.image.description="CheckIn — backend service учёта посещаемости студентов" \
      org.opencontainers.image.version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    HOST=0.0.0.0 \
    HTTP_PORT=8080

# Непривилегированный пользователь — приложение не работает от root
RUN groupadd --system app && useradd --system --gid app --no-create-home app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY --chown=app:app cmd/ ./cmd/
COPY --chown=app:app internal/ ./internal/

USER app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"HTTP_PORT\", \"8080\")}/api/v1/health', timeout=2)" || exit 1

CMD ["python", "-m", "cmd.app"]
