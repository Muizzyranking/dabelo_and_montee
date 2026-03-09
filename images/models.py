from __future__ import annotations

import uuid

from django.db import models


class ImageStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    READY = "ready", "Ready"
    FAILED = "failed", "Failed"


class Image(models.Model):
    """
    Central image record. All apps reference this via FK.
    Bytes live in the storage backend — this model only stores
    the key needed to retrieve/serve them.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=500, unique=True)
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="SHA-256 of processed bytes — used for deduplication.",
    )
    brand = models.CharField(max_length=20, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=10,
        choices=ImageStatus.choices,
        default=ImageStatus.PENDING,
    )
    mime_type = models.CharField(max_length=50, default="image/jpeg")

    # Dimensions and size — populated at upload time from processed bytes.
    width = models.PositiveIntegerField(
        null=True, blank=True, help_text="Width in pixels after processing."
    )
    height = models.PositiveIntegerField(
        null=True, blank=True, help_text="Height in pixels after processing."
    )
    file_size = models.PositiveIntegerField(
        null=True, blank=True, help_text="Size of processed bytes in bytes."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.key} [{self.status}]"

    @property
    def serve_url(self) -> str:
        from django.urls import reverse

        return reverse("image_serve", kwargs={"image_id": str(self.id)})

    @property
    def url(self) -> str:
        return self.serve_url
