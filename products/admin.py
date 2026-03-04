from django.contrib import admin

from products.models import (
    Category,
    Product,
    ProductAttribute,
    ProductImage,
    ProductVariation,
)

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductImage)
admin.site.register(ProductVariation)
admin.site.register(ProductAttribute)
