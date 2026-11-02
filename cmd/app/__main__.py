import uvicorn

from internal.config.settings import settings


def main() -> None:
    uvicorn.run(
        "cmd.app.main:app",
        host=settings.host,
        port=settings.port,
        proxy_headers=True,
    )


if __name__ == "__main__":
    main()
