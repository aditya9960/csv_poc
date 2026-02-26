import os
from datetime import datetime
import pathlib
import hashlib
from app.core.config import settings
from .base import StorageBackend

CHUNK_SIZE = 1024 * 1024

class LocalStorage(StorageBackend):
    """
    for storing & retriving file locally on path as per configs
    """
    async def save_file(self, file_id: str, upload_file) -> str:
        os.makedirs(settings.storage_path, exist_ok=True)
        # adding timestamp for filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        original = pathlib.Path(upload_file.filename).stem
        filename = f"{original}_{timestamp}_{file_id}.csv"
        path = os.path.join(settings.storage_path, filename)
        # adding checksum
        sha256 = hashlib.sha256()

        with open(path, "wb") as buffer:
            while chunk := upload_file.file.read(CHUNK_SIZE):
                sha256.update(chunk)
                buffer.write(chunk)
        checksum = sha256.hexdigest()
        return path, checksum
    # not required
    async def get_file_path(self, file_id: str) -> str:
        pass
        # return os.path.join(settings.storage_path, f"{file_id}.csv")

