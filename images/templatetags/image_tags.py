from django import template
from images.utils import get_image_url, get_image_or_placeholder

register = template.Library()


@register.filter(name="image_url")
def image_url(image_instance, size: str = "medium") -> str:
    """
    Return the URL of a ManagedImage at the given size.

    Usage:  {{ product.image|image_url:'thumbnail' }}
    """
    return get_image_url(image_instance, size)


@register.filter(name="image_or_placeholder")
def image_or_placeholder(image_instance, placeholder: str = "") -> str:
    """
    Return the image URL or a placeholder if no image is set.

    Usage:  {{ product.image|image_or_placeholder:'/static/images/placeholder.jpg' }}
    """
    return get_image_or_placeholder(image_instance, placeholder=placeholder)


@register.simple_tag
def image_src(image_instance, size: str = "medium", placeholder: str = "") -> str:
    """
    Simple tag version for more readable syntax.

    Usage:  {% image_src product.image 'medium' '/static/images/placeholder.jpg' %}
    """
    return get_image_or_placeholder(image_instance, size=size, placeholder=placeholder)
