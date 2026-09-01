import os
import re
import uuid
import asyncio
from pathlib import Path
from typing import Optional
from app.config import settings
from app.storage.base import DocumentStorage
from app.core.exceptions import BadRequestException


class LocalDocumentStorage(DocumentStorage):
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or settings.UPLOAD_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)
        cleaned = re.sub(r"\.{2,}", ".", cleaned)
        return cleaned

    def _get_secure_path(self, relative_or_absolute: str) -> Path:
        target = Path(relative_or_absolute)
        if not target.is_absolute():
            target = (self.base_dir / relative_or_absolute).resolve()
        else:
            target = target.resolve()
        
        upload_resolved = self.base_dir.resolve()
        mock_resolved = settings.MOCK_DATA_DIR.resolve()
        workspace_resolved = settings.BASE_DIR.resolve()
        
        try:
            target.relative_to(upload_resolved)
        except ValueError:
            try:
                target.relative_to(mock_resolved)
            except ValueError:
                try:
                    target.relative_to(workspace_resolved)
                except ValueError:
                    raise BadRequestException(f"Invalid file path: {relative_or_absolute}")
        
        return target

    def _write_bytes(self, target_path: Path, file_bytes: bytes) -> None:
        with open(target_path, "wb") as f:
            f.write(file_bytes)

    def _read_bytes(self, target_path: Path) -> bytes:
        with open(target_path, "rb") as f:
            return f.read()

    async def save_file(
        self,
        file_bytes: bytes,
        filename: str,
        subdirectory: str = "",
    ) -> str:
        sanitized = self._sanitize_filename(filename)
        unique_name = f"{uuid.uuid4().hex[:8]}_{sanitized}"
        
        dest_dir = self.base_dir
        if subdirectory:
            sub_sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", subdirectory)
            dest_dir = self.base_dir / sub_sanitized
        
        dest_dir.mkdir(parents=True, exist_ok=True)
        target_path = dest_dir / unique_name
        
        await asyncio.to_thread(self._write_bytes, target_path, file_bytes)
        return str(target_path)

    async def get_file_bytes(self, file_path: str) -> bytes:
        secure_path = self._get_secure_path(file_path)
        if not secure_path.exists() or not secure_path.is_file():
            raise BadRequestException(f"File not found: {file_path}")
            
        return await asyncio.to_thread(self._read_bytes, secure_path)

    async def file_exists(self, file_path: str) -> bool:
        try:
            secure_path = self._get_secure_path(file_path)
            return secure_path.exists() and secure_path.is_file()
        except Exception:
            return False

    async def delete_file(self, file_path: str) -> bool:
        try:
            secure_path = self._get_secure_path(file_path)
            if secure_path.exists() and secure_path.is_file():
                secure_path.unlink()
                return True
            return False
        except Exception:
            return False
