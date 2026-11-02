"""Загрузка и проверка конфигурации приложения из переменных окружения."""

from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CheckIn Backend Service"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = Field(default=8080, validation_alias="HTTP_PORT", ge=1, le=65535)

    db_host: str = Field(validation_alias="DB_HOST", min_length=1)
    db_port: int = Field(default=5432, validation_alias="DB_PORT", ge=1, le=65535)
    db_user: str = Field(validation_alias="DB_USER", min_length=1)
    db_password: SecretStr = Field(validation_alias="DB_PASSWORD", min_length=1)
    db_name: str = Field(validation_alias="DB_NAME", min_length=1)
    db_max_conns: int = Field(default=10, validation_alias="DB_MAX_CONNS", ge=1, le=100)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def database_url(self) -> str:
        """Собирает DSN, корректно экранируя логин, пароль и имя БД."""
        from urllib.parse import quote

        user = quote(self.db_user, safe="")
        password = quote(self.db_password.get_secret_value(), safe="")
        database = quote(self.db_name, safe="")
        return (
            f"postgresql://{user}:{password}@{self.db_host}:{self.db_port}/"
            f"{database}?connect_timeout=3"
        )


def load_settings() -> Settings:
    """Возвращает конфигурацию с понятной ошибкой при неверных настройках."""
    try:
        return Settings()
    except ValidationError as exc:
        missing = []
        for error in exc.errors():
            loc = error.get("loc", ())
            if loc:
                missing.append(str(loc[0]).upper())
        names = ", ".join(sorted(set(missing))) or "неизвестные параметры"
        raise RuntimeError(
            f"Ошибка конфигурации: проверьте обязательные переменные окружения: {names}. "
            "Сверьтесь с файлом .env.example."
        ) from exc


settings = load_settings()
