from django.contrib import admin

from products.models import (
    Category,
    CustomOrderRequest,
    Product,
    ProductAttribute,
    ProductGalleryImage,
    ProductVariation,
)

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductGalleryImage)
admin.site.register(ProductVariation)
admin.site.register(ProductAttribute)
admin.site.register(CustomOrderRequest)
