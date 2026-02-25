from enum import Enum
from pydantic_settings import BaseSettings

# TODO class Config from Settings

class Settings(BaseSettings):
    app_name: str = "csv-service"
    postgres_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/files"
    redis_url: str = ""
    storage_path: str = "/data/files"  # TODO
    default_page_size: int = 20

    class Config:
        env_file = ".env"

settings = Settings()
