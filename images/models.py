import os
import uuid

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


def image_upload_path(instance, filename):
    """Dynamic upload path: images/<brand_type>/<uuid>.<ext>"""
    ext = os.path.splitext(filename)[1].lower()
    return f"images/{instance.brand_type}/{uuid.uuid4().hex}{ext}"


class BrandType(models.TextChoices):
    DABELO = "dabelo", "Dabelo Café"
    MOTEE = "motee", "Motee Cakes"
    JOINT = "joint", "Joint / Shared"


class ManagedImage(models.Model):
    """
    A processed, stored image with multiple size variants.

    Size variants are stored as separate file fields.
    The 'original' field holds the source; thumbnail and medium
    are auto-generated on save via signals.py.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand_type = models.CharField(
        max_length=10,
        choices=BrandType.choices,
        default=BrandType.JOINT,
        db_index=True,
    )

    original = models.ImageField(upload_to=image_upload_path)
    thumbnail = models.ImageField(upload_to="images/variants/thumbnails/", blank=True)
    medium = models.ImageField(upload_to="images/variants/medium/", blank=True)

    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.CharField(max_length=500, blank=True)
    is_watermarked = models.BooleanField(default=False)
    file_size_bytes = models.PositiveIntegerField(null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Image"
        verbose_name_plural = "Images"
        indexes = [
            models.Index(fields=["brand_type", "uploaded_at"]),
        ]

    def __str__(self):
        return f"{self.get_brand_type_display()} image — {self.id}"

    def get_brand_type_display(self):
        return self.brand_type

    def get_url(self, size: str = "medium") -> str:
        """
        Get the URL for a specific size variant.
        Falls back gracefully: medium → thumbnail → original.

        Usage in templates:  {{ image.get_url:'medium' }}
        Usage in Python:     image.get_url('thumbnail')
        """
        size_map = {
            "thumbnail": self.thumbnail,
            "medium": self.medium,
            "original": self.original,
        }
        field = size_map.get(size, self.medium)
        if field and field.name:
            return field.url

        for fallback in ["medium", "thumbnail", "original"]:
            f = size_map[fallback]
            if f and f.name:
                return f.url

        return ""


@receiver(post_delete, sender=ManagedImage)
def delete_image_files(sender, instance, **kwargs):
    """Clean up all variant files when a ManagedImage is deleted."""
    for field in [instance.original, instance.thumbnail, instance.medium]:
        if field and field.name:
            try:
                field.delete(save=False)
            except Exception:
                pass


# Create your models here.
