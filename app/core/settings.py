
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Assistant"
    app_env: str = "development"
    app_debug: bool = True
    database_url: str = "postgresql://user:password@localhost:5432/personal_assistant"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()