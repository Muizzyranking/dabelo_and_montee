def get_image_url(image_instance, size: str = "medium") -> str:
    """
    Get a URL for a ManagedImage at a specific size.
    """
    if image_instance is None:
        return ""
    return image_instance.get_url(size)


def get_image_or_placeholder(
    image_instance, size: str = "medium", placeholder: str = ""
) -> str:
    """
    Get an image URL or fall back to a placeholder URL.

    Useful in templates where a fallback image is needed.
    """
    url = get_image_url(image_instance, size)
    return url if url else placeholder


def image_url_filter(image_instance, size: str = "medium") -> str:
    """
    Django template filter version of get_image_url.
    Registered in templatetags/image_tags.py.
    """
    return get_image_url(image_instance, size)
