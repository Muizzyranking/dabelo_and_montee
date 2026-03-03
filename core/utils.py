from django.http import HttpRequest


def set_brand(request: HttpRequest, brand_name) -> HttpRequest:
    if brand_name is None:
        brand_name = "dabelo"
    brand = brand_name.lower()
    request.brand = brand  # type: ignore
    return request
