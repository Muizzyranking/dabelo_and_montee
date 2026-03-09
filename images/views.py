from __future__ import annotations

import logging

from django.http import Http404, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import condition

from .models import Image, ImageStatus
from .services import ImageService

logger = logging.getLogger(__name__)

BROWSER_CACHE_MAX_AGE = 60 * 60 * 24 * 7  # 1 week


def _etag(request, image_id):
    try:
        img = Image.objects.get(pk=image_id)
        return f'"{img.id}-{img.updated_at.timestamp()}"'
    except Image.DoesNotExist:
        return None


def _last_modified(request, image_id):
    try:
        return Image.objects.get(pk=image_id).updated_at
    except Image.DoesNotExist:
        return None


@cache_control(public=True, max_age=BROWSER_CACHE_MAX_AGE)
@condition(etag_func=_etag, last_modified_func=_last_modified)
def serve_image(request, image_id: str) -> HttpResponse:
    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        raise Http404

    if image.status == ImageStatus.PENDING:
        return HttpResponse(status=202, headers={"Retry-After": "5"})

    if image.status == ImageStatus.FAILED:
        raise Http404

    try:
        data = ImageService.load(image)
    except FileNotFoundError:
        raise Http404

    return HttpResponse(data, content_type=image.mime_type)
