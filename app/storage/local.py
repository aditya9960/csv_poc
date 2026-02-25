import os
from app.core.config import settings
from .base import StorageBackend

CHUNK_SIZE = 1024 * 1024

class LocalStorage(StorageBackend):
    """
    for storing & retriving file locally on path as per configs
    """
    async def save_file(self, file_id: str, upload_file) -> str:
        os.makedirs(settings.storage_path, exist_ok=True)
        path = os.path.join(settings.storage_path, f"{file_id}.csv")
        with open(path, "wb") as buffer:
            while chunk := upload_file.file.read(CHUNK_SIZE):
                buffer.write(chunk)
        return path

    async def get_file_path(self, file_id: str) -> str:
        return os.path.join(settings.storage_path, f"{file_id}.csv")