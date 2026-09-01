from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional


class DocumentStorage(ABC):
    @abstractmethod
    async def save_file(
        self,
        file_bytes: bytes,
        filename: str,
        subdirectory: str = "",
    ) -> str:
        """Saves file bytes and returns the stored file path."""
        pass

    @abstractmethod
    async def get_file_bytes(self, file_path: str) -> bytes:
        """Retrieves raw bytes from storage path."""
        pass

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Checks if file exists in storage."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Deletes file from storage."""
        pass
