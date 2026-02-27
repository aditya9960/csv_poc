from abc import ABC, abstractmethod

class StorageBackend(ABC):
    """
    defining abstract for future modifications
    """
    @abstractmethod
    async def save_file(self, file_id: str, file) -> str:
        pass

    @abstractmethod
    async def get_file_path(self, file_id: str) -> str:
        pass