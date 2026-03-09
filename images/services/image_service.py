from __future__ import annotations

import hashlib
import logging
from typing import Literal

from django.conf import settings
from django.core.exceptions import ValidationError

from images.models import Image, ImageStatus

from .processor import ImageProcessor
from .storage import get_storage_backend

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES: int = getattr(settings, "IMAGE_MAX_UPLOAD_BYTES", 10 * 1024 * 1024)


def _validate_size(file_data: bytes) -> None:
    """Raise ValidationError if file_data exceeds the configured limit."""
    if len(file_data) > MAX_UPLOAD_BYTES:
        raise ValidationError(
            f"Image exceeds the maximum upload size of "
            f"{MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
        )


def _ext_from_format(output_format: str) -> str:
    """Return a file extension for the given Pillow output format string."""
    return "jpg" if output_format.upper() == "JPEG" else output_format.lower()


class ImageService:
    """Single entry point for all image operations across the project."""

    @classmethod
    def upload(
        cls,
        file_data: bytes,
        *,
        brand: str | Literal[False] = False,
        alt_text: str = "",
        output_format: str = "JPEG",
    ) -> Image:
        """Process and store an image synchronously."""
        _validate_size(file_data)

        result = ImageProcessor.process(
            file_data,
            brand=brand,
            watermark=bool(brand),
            output_format=output_format,
        )

        # Dedup against processed bytes
        file_hash = hashlib.sha256(result.data).hexdigest()
        existing = Image.objects.filter(
            file_hash=file_hash, status=ImageStatus.READY
        ).first()
        if existing:
            logger.info(
                "Dedup hit hash=%s — reusing image %s", file_hash[:12], existing.id
            )
            return existing

        storage = get_storage_backend()
        key = storage.make_key(brand=brand or "", ext=_ext_from_format(output_format))
        storage.save(key, result.data, content_type=result.mime_type)

        image = Image.objects.create(
            key=key,
            file_hash=file_hash,
            brand=brand or "",
            alt_text=alt_text,
            status=ImageStatus.READY,
            mime_type=result.mime_type,
            width=result.info.width,
            height=result.info.height,
            file_size=result.info.file_size,
        )

        logger.info(
            "Uploaded image %s (hash=%s, %sx%s, %s bytes)",
            image.id,
            file_hash[:12],
            result.info.width,
            result.info.height,
            result.info.file_size,
        )
        return image

    @classmethod
    def upload_async(
        cls,
        file_data: bytes,
        *,
        brand: str | Literal[False] = False,
        alt_text: str = "",
        output_format: str = "JPEG",
    ) -> Image:
        """
        Defer processing to a Celery worker. Returns a PENDING Image immediately.
        Swap upload() → upload_async() to go async; nothing else changes for callers.
        """
        _validate_size(file_data)

        storage = get_storage_backend()
        ext = _ext_from_format(output_format)
        key = storage.make_key(brand=brand or "", ext=ext)

        # mime_type is left blank — the task will fill it in once processing is done.
        image = Image.objects.create(
            key=key,
            brand=brand or "",
            alt_text=alt_text,
            status=ImageStatus.PENDING,
            mime_type="",
        )

        from images.tasks import process_image_task

        process_image_task.delay(  # type: ignore[attr-defined]
            image_id=str(image.id),
            file_data=file_data,
            brand=brand or "",
            output_format=output_format,
        )

        return image

    @classmethod
    def delete(cls, image: Image) -> None:
        """Remove from storage, delete DB record."""
        try:
            get_storage_backend().delete(image.key)
        except Exception as exc:
            logger.warning("Storage delete failed key=%s: %s", image.key, exc)

        image.delete()

    @classmethod
    def load(cls, image: Image) -> bytes:
        """Load raw processed bytes from storage. Used by the serve view."""
        return get_storage_backend().load(image.key)
