from __future__ import annotations

import hashlib
import logging

from celery import shared_task

from .models import Image, ImageStatus
from .services import ImageProcessor, get_storage_backend

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="images.tasks.process_image_task",
)
def process_image_task(
    self,
    *,
    image_id: str,
    file_data: bytes,
    brand: str = "",
    output_format: str = "JPEG",
) -> None:
    """
    Celery task: process and store an image that was created as PENDING.

    On dedup: the PENDING record is updated to mirror the existing READY image
    so any caller already holding this image_id continues to get a valid record.

    Retries up to 3 times on transient failures; marks FAILED only when all
    retries are exhausted.
    """
    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        logger.error("process_image_task: Image %s not found — nothing to do", image_id)
        return

    try:
        # Watermark is applied whenever a brand is provided.
        result = ImageProcessor.process(
            file_data,
            brand=brand or False,
            watermark=bool(brand),
            output_format=output_format,
        )

        file_hash = hashlib.sha256(result.data).hexdigest()

        existing = (
            Image.objects.filter(file_hash=file_hash, status=ImageStatus.READY)
            .exclude(pk=image_id)
            .first()
        )
        if existing:
            logger.info(
                "Async dedup hit hash=%s — updating image %s to mirror %s",
                file_hash[:12],
                image_id,
                existing.id,
            )
            image.key = existing.key
            image.file_hash = existing.file_hash
            image.mime_type = existing.mime_type
            image.width = existing.width
            image.height = existing.height
            image.file_size = existing.file_size
            image.status = ImageStatus.READY
            image.save(
                update_fields=[
                    "key",
                    "file_hash",
                    "mime_type",
                    "width",
                    "height",
                    "file_size",
                    "status",
                    "updated_at",
                ]
            )
            return

        storage = get_storage_backend()
        storage.save(image.key, result.data, content_type=result.mime_type)

        image.file_hash = file_hash
        image.mime_type = result.mime_type
        image.width = result.info.width
        image.height = result.info.height
        image.file_size = result.info.file_size
        image.status = ImageStatus.READY
        image.save(
            update_fields=[
                "file_hash",
                "mime_type",
                "width",
                "height",
                "file_size",
                "status",
                "updated_at",
            ]
        )

        logger.info("Image %s processed and stored successfully", image_id)

    except Exception as exc:
        logger.exception("Image %s processing failed: %s", image_id, exc)
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(
                "Image %s permanently failed after %s retries",
                image_id,
                self.max_retries,
            )
            try:
                image.status = ImageStatus.FAILED
                image.save(update_fields=["status", "updated_at"])
            except Exception as save_exc:
                logger.error(
                    "Image %s — could not update status to FAILED: %s",
                    image_id,
                    save_exc,
                )
