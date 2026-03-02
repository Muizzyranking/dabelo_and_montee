from django.contrib import admin
from .models import ManagedImage


@admin.register(ManagedImage)
class ManagedImageAdmin(admin.ModelAdmin):
    list_display = ["id", "brand_type", "alt_text", "uploaded_at", "is_watermarked"]
    list_filter = ["brand_type", "is_watermarked"]
    search_fields = ["alt_text", "caption"]
    readonly_fields = [
        "id",
        "uploaded_at",
        "updated_at",
        "file_size_bytes",
        "thumbnail",
        "medium",
    ]
    fieldsets = (
        (
            "Image File",
            {"fields": ("original", "thumbnail", "medium")},
        ),
        (
            "Metadata",
            {"fields": ("brand_type", "alt_text", "caption", "is_watermarked")},
        ),
        (
            "System",
            {
                "fields": ("id", "file_size_bytes", "uploaded_at", "updated_at"),
                "classes": ("collapse"),
            },
        ),
    )
