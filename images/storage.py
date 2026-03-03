from django.core.files.storage import FileSystemStorage


class LocalImageStorage(FileSystemStorage):
    """
    Default local storage. Saves to MEDIA_ROOT/images/.
    """

    def __init__(self, *args, **kwargs):
        from django.conf import settings
        import os

        location = os.path.join(settings.MEDIA_ROOT, "images")
        base_url = settings.MEDIA_URL + "images/"
        super().__init__(location=location, base_url=base_url, *args, **kwargs)


def get_storage_backend():
    """
    Returns the active storage backend instance.
    To switch backends, change IMAGE_STORAGE_BACKEND in settings.py.
    """
    from django.conf import settings
    from django.utils.module_loading import import_string

    backend_path = getattr(settings, "IMAGE_STORAGE_BACKEND", None)
    if backend_path:
        BackendClass = import_string(backend_path)
        return BackendClass()
    return LocalImageStorage()
