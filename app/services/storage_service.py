"""Secure file storage for uploaded resumes."""
from __future__ import annotations

import os
import re
import uuid

from fastapi import UploadFile

from app.core.config import settings

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]")


class UploadValidationError(Exception):
    pass


class StorageService:
    def __init__(self) -> None:
        self.base_dir = settings.upload_dir
        os.makedirs(self.base_dir, exist_ok=True)

    @staticmethod
    def _sanitise(filename: str) -> str:
        name = os.path.basename(filename or "resume.pdf")
        return _SAFE_NAME.sub("_", name)[:120]

    def validate(self, upload: UploadFile, size: int) -> None:
        # Type check (content-type + extension)
        filename = (upload.filename or "").lower()
        if not filename.endswith(".pdf"):
            raise UploadValidationError("Only PDF files are accepted.")
        if upload.content_type not in {"application/pdf", "application/octet-stream"}:
            raise UploadValidationError("Invalid content type; expected a PDF.")
        if size <= 0:
            raise UploadValidationError("The uploaded file is empty.")
        if size > settings.max_upload_size_bytes:
            raise UploadValidationError(
                f"File too large. Maximum size is {settings.max_upload_size_mb} MB."
            )

    def save(self, upload: UploadFile, content: bytes) -> tuple[str, int]:
        """Persist file content; returns (stored_path, size_bytes)."""
        safe = self._sanitise(upload.filename or "resume.pdf")
        unique = f"{uuid.uuid4().hex}_{safe}"
        path = os.path.join(self.base_dir, unique)
        with open(path, "wb") as fh:
            fh.write(content)
        return path, len(content)
