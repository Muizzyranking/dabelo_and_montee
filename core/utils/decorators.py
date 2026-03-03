from functools import wraps


def set_brand(brand_name=None):
    """
    Decorator to set request.brand.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if brand_name is not None:
                request.brand = brand_name.lower()
            else:
                name_lower = view_func.__name__.lower()
                if "dabelo" in name_lower:
                    request.brand = "dabelo"
                elif "montee" in name_lower:
                    request.brand = "montee"
                else:
                    request.brand = "default"
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if callable(brand_name):
        return decorator(brand_name)
    return decorator
