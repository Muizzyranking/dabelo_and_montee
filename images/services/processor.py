from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from django.conf import settings
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont

logger = logging.getLogger(__name__)


_MAX_DIMENSIONS: tuple[int, int] = getattr(
    settings, "IMAGE_MAX_DIMENSIONS", (1920, 1920)
)
_JPEG_QUALITY: int = getattr(settings, "IMAGE_JPEG_QUALITY", 82)
_WATERMARK_OPACITY: int = getattr(settings, "IMAGE_WATERMARK_OPACITY", 200)
_WATERMARK_FONT_FRACTION: float = getattr(
    settings, "IMAGE_WATERMARK_FONT_FRACTION", 0.08
)

_FONTS_DIR = Path(settings.BASE_DIR) / "static" / "fonts"

_BRAND_FONTS: dict[str, str] = {
    "dabelo": str(_FONTS_DIR / "Cormorant-Regular.ttf"),
    "montee": str(_FONTS_DIR / "PlayfairDisplay-Regular.ttf"),
}

_BRAND_WATERMARK_TEXT: dict[str, str] = getattr(
    settings,
    "IMAGE_WATERMARK_TEXTS",
    {
        "dabelo": "Dabelo Café",
        "montee": "Motee Cakes",
    },
)

_MIME_TYPE_MAP: dict[str, str] = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}


@dataclass(frozen=True)
class ImageInfo:
    width: int
    height: int
    mime_type: str
    file_size: int


@dataclass(frozen=True)
class ProcessedImage:
    data: bytes
    mime_type: str
    info: ImageInfo


class ImageProcessor:
    """
    Pure Pillow operations — no Django, no storage, no DB.
    Takes bytes in, returns bytes out.
    """

    _ALLOWED_FORMATS: frozenset[str] = frozenset(_MIME_TYPE_MAP.keys())

    @classmethod
    def process(
        cls,
        file_data: bytes,
        *,
        brand: str | Literal[False] = False,
        watermark: bool = False,
        output_format: str = "JPEG",
    ) -> ProcessedImage:
        """
        Full pipeline: open → normalise → resize → watermark → encode.
        Returns a ProcessedImage with the final bytes, mime type, and metadata.
        """
        fmt = output_format.upper()
        if fmt not in cls._ALLOWED_FORMATS:
            raise ValueError(f"Unsupported output format: {output_format!r}")

        image = cls._open(file_data)
        image = cls._resize(image, _MAX_DIMENSIONS)

        if watermark and brand:
            image = cls._apply_watermark(image, brand=str(brand))

        data, mime_type = cls._encode(image, fmt, _JPEG_QUALITY)

        info = ImageInfo(
            width=image.width,
            height=image.height,
            mime_type=mime_type,
            file_size=len(data),
        )

        return ProcessedImage(data=data, mime_type=mime_type, info=info)

    @staticmethod
    def _open(file_data: bytes) -> PILImage.Image:
        """Open and normalise image to RGB/RGBA. Raises ValueError on corrupt input."""
        try:
            img = PILImage.open(io.BytesIO(file_data))
            img.load()  # force decode — catches corrupt files early
        except Exception as exc:
            raise ValueError(f"Invalid or unreadable image file: {exc}") from exc

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        return img

    @staticmethod
    def _resize(img: PILImage.Image, max_dims: tuple[int, int]) -> PILImage.Image:
        """Scale down proportionally if larger than max_dims. Never upscales."""
        img.thumbnail(max_dims, PILImage.Resampling.LANCZOS)
        return img

    @staticmethod
    def _apply_watermark(img: PILImage.Image, *, brand: str) -> PILImage.Image:
        """Draw a centered, semi-transparent brand text watermark."""
        text = _BRAND_WATERMARK_TEXT.get(brand, brand.capitalize())
        font_path = _BRAND_FONTS.get(brand)
        w, h = img.size
        font_size = max(20, int(min(w, h) * _WATERMARK_FONT_FRACTION))

        font: ImageFont.FreeTypeFont | ImageFont.ImageFont
        if font_path and Path(font_path).exists():
            try:
                font = ImageFont.truetype(font_path, font_size)
            except OSError:
                logger.warning(
                    "Could not load font %s — falling back to default", font_path
                )
                font = ImageFont.load_default()
        else:
            logger.warning(
                "Font not found for brand %r — falling back to default", brand
            )
            font = ImageFont.load_default()

        overlay = PILImage.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (w - text_w) / 2
        y = (h - text_h) / 2
        draw.text((x, y), text, font=font, fill=(255, 255, 255, _WATERMARK_OPACITY))

        base = img.convert("RGBA")
        combined = PILImage.alpha_composite(base, overlay)
        logger.debug("Watermark applied for brand=%r", brand)
        return combined.convert("RGB")

    @staticmethod
    def _encode(img: PILImage.Image, fmt: str, quality: int) -> tuple[bytes, str]:
        """Encode the image to the target format with format-specific optimisation."""
        if fmt == "JPEG" and img.mode == "RGBA":
            background = PILImage.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background

        buf = io.BytesIO()
        save_kwargs: dict = {"format": fmt, "optimize": True}

        if fmt == "JPEG":
            save_kwargs["quality"] = quality
            save_kwargs["progressive"] = True
        elif fmt == "PNG":
            save_kwargs["compress_level"] = 6
        elif fmt == "WEBP":
            save_kwargs["quality"] = quality
            save_kwargs["method"] = 6

        img.save(buf, **save_kwargs)
        return buf.getvalue(), _MIME_TYPE_MAP[fmt]
