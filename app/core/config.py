from enum import Enum
from pydantic_settings import BaseSettings

# TODO class Config from Settings

class Settings(BaseSettings):
    app_name: str = "csv-service"
    postgres_url: str = ""
    redis_url: str = ""
    storage_path: str = ""
    default_page_size: int = 20

    class Config:
        env_file = ".env"

settings = Settings()
