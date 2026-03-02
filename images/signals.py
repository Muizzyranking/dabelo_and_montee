import logging

from django.core.files.base import ContentFile
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _generate_variants(instance):
    """
    Generate thumbnail and medium variants from the original image.
    Called when a new original is uploaded.
    """
    from .services import generate_all_variants

    if not instance.original or not instance.original.name:
        return

    try:
        instance.original.seek(0)
        variants = generate_all_variants(instance.original)

        base_name = f"{instance.id}"

        # Save thumbnail variant
        if "thumbnail" in variants:
            instance.thumbnail.save(
                f"{base_name}_thumb.jpg",
                ContentFile(variants["thumbnail"]),
                save=False,
            )
            logger.info(f"Generated thumbnail for image {instance.id}")

        if "medium" in variants:
            instance.medium.save(
                f"{base_name}_medium.jpg",
                ContentFile(variants["medium"]),
                save=False,
            )
            logger.info(f"Generated medium variant for image {instance.id}")

    except Exception as e:
        logger.error(f"Failed to generate variants for image {instance.id}: {e}")


_original_field_tracker = {}


@receiver(pre_save, sender="images.ManagedImage")
def track_original_change(sender, instance, **kwargs):
    """Record the previous original filename before save."""
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            _original_field_tracker[instance.pk] = old.original.name
        except sender.DoesNotExist:
            _original_field_tracker[instance.pk] = None


@receiver(post_save, sender="images.ManagedImage")
def generate_image_variants(sender, instance, created, **kwargs):
    """
    After save: generate variants if this is a new image
    or if the original file has changed.
    """
    if not instance.original or not instance.original.name:
        return

    old_name = _original_field_tracker.pop(instance.pk, None)
    original_changed = created or (old_name != instance.original.name)

    if original_changed:
        _generate_variants(instance)
        sender.objects.filter(pk=instance.pk).update(
            thumbnail=instance.thumbnail.name if instance.thumbnail else "",
            medium=instance.medium.name if instance.medium else "",
        )
