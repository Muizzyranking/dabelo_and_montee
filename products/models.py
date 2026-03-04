import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class BrandChoices(models.TextChoices):
    DABELO = "dabelo", "Dabelo Café"
    MONTEE = "montee", "Montee Cakes"


class ProductType(models.TextChoices):
    SIMPLE = "simple", "Simple (single price)"
    VARIABLE = "variable", "Variable (multiple variations)"


class Category(models.Model):
    brand = models.CharField(max_length=20, choices=BrandChoices.choices)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.get_brand_display()} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop_category", kwargs={"slug": self.slug})


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.CharField(max_length=20, choices=BrandChoices.choices)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    product_type = models.CharField(
        max_length=20, choices=ProductType.choices, default=ProductType.SIMPLE
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300, blank=True)

    # Pricing — only used for simple products. Variable products use ProductVariation.
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # For Montee "Get a Quote" cakes
    is_quote_only = models.BooleanField(
        default=False, help_text="Show 'Get a Quote' instead of Add to Cart"
    )

    # Stock
    in_stock = models.BooleanField(default=True)

    # Visibility
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def display_price(self):
        """Returns lowest variation price for variable products, or the simple price."""
        if self.product_type == ProductType.VARIABLE:
            variation = self.variations.filter(in_stock=True).order_by("price").first()
            return variation.price if variation else None
        return self.price

    @property
    def gallery_images(self):
        """All images including variation images, ordered."""
        return self.images.all().order_by("order", "-is_primary")


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-is_primary"]

    def __str__(self):
        return f"{self.product.name} — image {self.order}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(
                pk=self.pk
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariation(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variations"
    )
    name = models.CharField(
        max_length=100, help_text="e.g. '500ml', 'Medium (serves 10)', 'Red Velvet'"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to="variations/",
        null=True,
        blank=True,
        help_text="Optional — shown in gallery and selected when this variation is chosen",
    )
    in_stock = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "price"]

    def __str__(self):
        return f"{self.product.name} — {self.name}"


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="attributes"
    )
    name = models.CharField(
        max_length=100, help_text="e.g. 'Volume', 'Contains', 'Allergens'"
    )
    value = models.CharField(
        max_length=300, help_text="e.g. '500ml', 'Mango, Pineapple', 'Contains nuts'"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.product.name} — {self.name}: {self.value}"


class CustomOrderRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_REVIEW = "in_review", "In Review"
        QUOTED = "quoted", "Quoted"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    # Customer info
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # Request details
    occasion = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    budget = models.CharField(
        max_length=100, blank=True, help_text="Customer's stated budget range"
    )
    delivery_date = models.DateField(null=True, blank=True)

    # Which product page they came from (optional)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_requests",
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    admin_notes = models.TextField(
        blank=True, help_text="Internal notes — not shown to customer"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Quote request from {self.name} ({self.email}) — {self.created_at.date()}"
        )


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PROCESSING = "processing", "Processing"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="orders"
    )
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    # Delivery address snapshot
    delivery_name = models.CharField(max_length=200)
    delivery_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=100)
    delivery_state = models.CharField(max_length=100)

    # Payment
    paystack_ref = models.CharField(max_length=100, blank=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        """
        Determine prefix from the brands in the cart items.
        Falls back to ORD if mixed or unknown.
        """
        import random
        import string

        suffix = "".join(random.choices(string.digits, k=5))
        return f"ORD-{suffix}"

    @property
    def status_color(self):
        return {
            "pending": "yellow",
            "confirmed": "blue",
            "processing": "purple",
            "delivered": "green",
            "cancelled": "red",
        }.get(self.status, "gray")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.SET_NULL, null=True)
    variation = models.ForeignKey(
        "ProductVariation", on_delete=models.SET_NULL, null=True, blank=True
    )

    # Snapshots — accurate history even if product changes later
    product_name = models.CharField(max_length=200)
    variation_name = models.CharField(max_length=100, blank=True)
    product_brand = models.CharField(max_length=20, blank=True)  # dabelo | montee
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.order.order_number} — {self.product_name}"
