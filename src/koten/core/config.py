from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Koten Backend"
    db_file: str = "data/koten.sqlite3"
    images_dir: str = "data/images"
    cors_allow_origins: list[str] = [
        "http://localhost:3006",
        "https://koten.ozkr.net",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
