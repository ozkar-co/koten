from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Koten Backend"
    db_file: str = "data/koten.sqlite3"
    images_dir: str = "data/images"
    cors_allow_origins: list[str] = [
        "http://localhost:3006",
        "http://127.0.0.1:3006",
        "https://koten.ozkr.net",
        "https://www.koten.ozkr.net",
    ]
    cors_allow_origin_regex: str = (
        r"https://([a-z0-9-]+\.)?ozkr\.net|https?://(localhost|127\.0\.0\.1)(:\\d+)?"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
