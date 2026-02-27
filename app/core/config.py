from enum import Enum
from pydantic_settings import BaseSettings

# TODO class Config from Settings

class Settings(BaseSettings):
    app_name: str = "csv-service"
    postgres_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/files"
    redis_url: str = "redis://redis:6379/0"
    storage_path: str = "/data/files"
    default_page_size: int = 20
    log_level: str = "INFO"
    running_tests: str = "0"

    class Config:
        env_file = ".env"

settings = Settings()
