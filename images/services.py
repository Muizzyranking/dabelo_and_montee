import io
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

IMAGE_SIZES = {
    "thumbnail": (150, 150),
    "medium": (600, 600),
}

# Compression quality (1-95, higher = better quality but larger file)
JPEG_QUALITY = 85
WEBP_QUALITY = 80


def process_image(file_obj, size_key: str) -> bytes:
    """
    Process an uploaded image file into a specific size variant.

    """
    try:
        img = Image.open(file_obj)

        # Convert to RGB (handles RGBA PNGs, palette images, etc.)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        if size_key != "original":
            max_size = IMAGE_SIZES[size_key]
            img.thumbnail(max_size, Image.LANCZOS)  # type: ignore

        output = io.BytesIO()
        img.save(output, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        output.seek(0)
        return output.read()

    except Exception as e:
        logger.error(f"Image processing failed for size '{size_key}': {e}")
        raise


def generate_all_variants(file_obj) -> dict:
    """
    Generate all configured size variants from an uploaded file.
    """
    variants = {}

    for size_key in [*IMAGE_SIZES.keys(), "original"]:
        file_obj.seek(0)
        variants[size_key] = process_image(file_obj, size_key)

    return variants


def add_watermark(image_bytes: bytes, text: str = "© Motee Cakes") -> bytes:
    """
    Add a diagonal text watermark to an image.

    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        watermark_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark_layer)

        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
            )
        except (IOError, OSError):
            font = ImageFont.load_default()

        # Draw text diagonally across the image
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Position at centre, semi-transparent
        x = (img.width - text_width) // 2
        y = (img.height - text_height) // 2
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 80))

        watermarked = Image.alpha_composite(img, watermark_layer).convert("RGB")
        output = io.BytesIO()
        watermarked.save(output, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        output.seek(0)
        return output.read()

    except Exception as e:
        logger.error(f"Watermarking failed: {e}")
        return image_bytes
