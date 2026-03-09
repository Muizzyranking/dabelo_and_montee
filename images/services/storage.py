from __future__ import annotations

import abc
import uuid
from pathlib import Path

from django.conf import settings


class StorageBackend(abc.ABC):
    """
    Abstract storage backend. Swap LocalBackend for S3Backend
    """

    @abc.abstractmethod
    def save(self, key: str, data: bytes, content_type: str = "image/jpeg") -> str:
        """Persist bytes under *key*. Returns the key."""

    @abc.abstractmethod
    def load(self, key: str) -> bytes:
        """Return raw bytes for *key*. Raises FileNotFoundError if missing."""

    @abc.abstractmethod
    def delete(self, key: str) -> None:
        """Remove the object at *key*. Silent if already gone."""

    @abc.abstractmethod
    def exists(self, key: str) -> bool:
        """Return True if *key* exists in the backend."""

    @staticmethod
    def make_key(brand: str = "", ext: str = "jpg") -> str:
        """
        Generates a unique storage key.
        e.g. "products/dabelo/2024/a3f9c21b.jpg"
        """
        prefix = f"products/{brand}" if brand else "products"
        return f"{prefix}/{uuid.uuid4().hex}.{ext}"


class LocalBackend(StorageBackend):
    """
    Stores images in MEDIA_ROOT/images/.
    Works out of the box for development and single-server production.
    Replace with S3Backend when moving to object storage.
    """

    def __init__(self) -> None:
        base = getattr(settings, "MEDIA_ROOT", "media")
        self._root = Path(base) / "images"
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        full = (self._root / key).resolve()
        if not str(full).startswith(str(self._root.resolve())):
            raise ValueError(f"Invalid key: {key!r}")
        return full

    def save(self, key: str, data: bytes, content_type: str = "image/jpeg") -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def load(self, key: str) -> bytes:
        path = self._path(key)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {key!r}")
        return path.read_bytes()

    def delete(self, key: str) -> None:
        path = self._path(key)
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    def exists(self, key: str) -> bool:
        return self._path(key).exists()


def get_storage_backend():
    from django.conf import settings

    backend_path = getattr(settings, "IMAGE_STORAGE_BACKEND", None)
    if backend_path:
        from django.utils.module_loading import import_string

        BackendClass = import_string(backend_path)
        return BackendClass()
    return LocalBackend()
