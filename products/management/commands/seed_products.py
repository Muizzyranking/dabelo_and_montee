from django.core.management.base import BaseCommand
from products.models import Category, Product, ProductVariation, ProductAttribute


DABELO_CATEGORIES = [
    {
        "name": "Fresh Juices",
        "slug": "fresh-juices",
        "description": "Cold-pressed daily. No preservatives, no added sugars, no colours.",
        "order": 1,
    },
    {
        "name": "Fresh Salads",
        "slug": "fresh-salads",
        "description": "Seasonal greens and proteins with signature dressings. Made to order.",
        "order": 2,
    },
    {
        "name": "Fruit Boxes",
        "slug": "fruit-boxes",
        "description": "Curated seasonal selections for families and offices.",
        "order": 3,
    },
]

MONTEE_CATEGORIES = [
    {
        "name": "Wedding Cakes",
        "slug": "wedding-cakes",
        "description": "Elegant tiered masterpieces designed around your vision.",
        "order": 1,
    },
    {
        "name": "Birthday Cakes",
        "slug": "birthday-cakes",
        "description": "Any theme, any size, any flavour.",
        "order": 2,
    },
    {
        "name": "Custom & Bespoke",
        "slug": "custom-bespoke",
        "description": "Your vision brought to life — unique shapes, flavours and edible art.",
        "order": 3,
    },
]

PRODUCTS = [
    # ── Dabelo ──────────────────────────────────────────────────────────────
    {
        "brand": "dabelo",
        "category_slug": "fresh-juices",
        "product_type": "variable",
        "is_featured": True,
        "name": "Berry Blast Juice",
        "short_description": "Cold-pressed raspberries, blueberries & strawberries. Pure, fresh, nothing added.",
        "description": "Our bestselling cold-pressed juice — a vibrant blend of raspberries, blueberries and strawberries. No water added. No sugar. Just pure, fresh fruit pressed daily.\n\nPerfect for breakfast, as a midday pick-me-up, or for children who need a healthy start to the day.",
        "variations": [
            {"name": "250ml", "price": "2000.00", "order": 1},
            {"name": "500ml", "price": "3500.00", "order": 2},
            {"name": "1 Litre", "price": "6000.00", "order": 3},
        ],
        "attributes": [
            {"name": "Contains", "value": "Raspberries, Blueberries, Strawberries"},
            {"name": "Preservatives", "value": "None"},
            {"name": "Added Sugar", "value": "None"},
            {"name": "Shelf Life", "value": "3 days refrigerated"},
            {"name": "Best Served", "value": "Chilled"},
        ],
    },
    {
        "brand": "dabelo",
        "category_slug": "fresh-juices",
        "product_type": "variable",
        "is_featured": True,
        "name": "Mango Tango Juice",
        "short_description": "Tropical mango, pineapple & banana. Cold-pressed, 100% pure.",
        "description": "A tropical escape in a bottle. Ripe mangoes, fresh pineapple and banana — cold-pressed with nothing else. Rich, smooth and 100% pure.\n\nA family favourite and one of our most requested juices.",
        "variations": [
            {"name": "250ml", "price": "2000.00", "order": 1},
            {"name": "500ml", "price": "3500.00", "order": 2},
            {"name": "1 Litre", "price": "6000.00", "order": 3, "in_stock": False},
        ],
        "attributes": [
            {"name": "Contains", "value": "Mango, Pineapple, Banana"},
            {"name": "Preservatives", "value": "None"},
            {"name": "Added Sugar", "value": "None"},
            {"name": "Shelf Life", "value": "3 days refrigerated"},
        ],
    },
    {
        "brand": "dabelo",
        "category_slug": "fresh-juices",
        "product_type": "simple",
        "is_featured": False,
        "name": "Pure Mango Juice",
        "price": "3500.00",
        "short_description": "One ingredient: 100% pure Nigerian mango. Nothing else.",
        "description": "Single ingredient. 100% pure mango. Nothing else.\n\nWe source the ripest Nigerian mangoes, press them fresh each morning and bottle immediately. No water, no sugar, no additives.",
        "attributes": [
            {"name": "Contains", "value": "100% Nigerian Mango"},
            {"name": "Volume", "value": "500ml"},
            {"name": "Preservatives", "value": "None"},
            {"name": "Shelf Life", "value": "3 days refrigerated"},
        ],
    },
    {
        "brand": "dabelo",
        "category_slug": "fresh-salads",
        "product_type": "simple",
        "is_featured": False,
        "name": "Signature Garden Salad",
        "price": "4500.00",
        "short_description": "Crisp seasonal greens with Dabelo house vinaigrette. Made to order.",
        "description": "Crisp romaine, cherry tomatoes, cucumber, red onion, carrots and our house vinaigrette. Served fresh and made to order.\n\nAvailable with grilled chicken, tuna or purely vegetarian.",
        "attributes": [
            {
                "name": "Contains",
                "value": "Romaine, Tomatoes, Cucumber, Red Onion, Carrots",
            },
            {"name": "Dressing", "value": "Dabelo house vinaigrette"},
            {"name": "Options", "value": "Vegetarian, Chicken, Tuna"},
        ],
    },
    {
        "brand": "dabelo",
        "category_slug": "fruit-boxes",
        "product_type": "simple",
        "is_featured": True,
        "name": "Weekly Family Fruit Box",
        "price": "12000.00",
        "short_description": "Seasonal fruits for a family of 4. Sourced locally, delivered weekly.",
        "description": "A curated selection of seasonal fruits from local Nigerian farmers — enough for a family of 4 for the week.\n\nTypically includes mangoes, bananas, watermelon, pineapple, pawpaw and seasonal additions. Delivered fresh every Monday.",
        "attributes": [
            {"name": "Serves", "value": "Family of 4 for 1 week"},
            {"name": "Delivery", "value": "Every Monday"},
            {
                "name": "Contents",
                "value": "Seasonal — mango, banana, watermelon, pineapple, pawpaw",
            },
            {"name": "Sourced", "value": "Local Nigerian farms"},
        ],
    },
    # ── Montee ──────────────────────────────────────────────────────────────
    {
        "brand": "montee",
        "category_slug": "birthday-cakes",
        "product_type": "variable",
        "is_featured": True,
        "name": "Classic Birthday Cake",
        "short_description": "Moist sponge, silky buttercream, personalised message. Available in multiple sizes.",
        "description": "Our most beloved birthday cake — moist vanilla sponge with silky buttercream frosting, delicate piping detail and a personalised message of your choice.\n\nAvailable in a range of sizes to suit intimate gatherings or large celebrations. Choose your flavour from vanilla, chocolate, red velvet or lemon.",
        "variations": [
            {"name": "Small (serves 10-15)", "price": "25000.00", "order": 1},
            {"name": "Medium (serves 20-30)", "price": "40000.00", "order": 2},
            {"name": "Large (serves 40-50)", "price": "65000.00", "order": 3},
        ],
        "attributes": [
            {"name": "Flavours", "value": "Vanilla, Chocolate, Red Velvet, Lemon"},
            {"name": "Frosting", "value": "Buttercream (Swiss meringue or American)"},
            {"name": "Lead Time", "value": "Order at least 48 hours in advance"},
            {
                "name": "Personalisation",
                "value": "Name, message and colour scheme included",
            },
        ],
    },
    {
        "brand": "montee",
        "category_slug": "wedding-cakes",
        "product_type": "simple",
        "is_featured": True,
        "is_quote_only": True,
        "name": "Wedding Tier Cake",
        "short_description": "Bespoke multi-tiered masterpiece for your forever day. Custom design consultation included.",
        "description": "A Montee wedding cake is a bespoke masterpiece — no two are ever the same. Each cake is designed in close consultation with the couple, from the tier structure and flavour to the finest decorative detail.\n\nWe use only premium ingredients: the finest butter, fresh Nigerian eggs, and hand-selected flavourings. Fresh flowers, fondant sculptures, gold leaf accents — all available on request.",
        "attributes": [
            {"name": "Tiers", "value": "2, 3 or 4 tier — custom"},
            {"name": "Lead Time", "value": "Minimum 2 weeks advance booking"},
            {"name": "Design", "value": "Full bespoke — consultation included"},
            {"name": "Delivery", "value": "Lagos delivery included"},
        ],
    },
    {
        "brand": "montee",
        "category_slug": "custom-bespoke",
        "product_type": "simple",
        "is_featured": False,
        "is_quote_only": True,
        "name": "Custom Celebration Cake",
        "short_description": "Any theme, any design. Tell us your vision and we will create it.",
        "description": "Have something specific in mind? Our custom order service lets you describe exactly what you want — theme, flavours, colours, size, budget — and our bakers will bring your vision to life.\n\nFill the quote form and we will respond within 24 hours with a personalised design and quote.",
        "attributes": [
            {"name": "Lead Time", "value": "Depends on complexity — minimum 1 week"},
            {
                "name": "Process",
                "value": "Quote request, consultation, confirmation, baking, delivery",
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample categories and products for development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing products and categories before seeding.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            ProductAttribute.objects.all().delete()
            ProductVariation.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("  Cleared."))

        # ── Categories ────────────────────────────────────────────────────
        self.stdout.write("\nCreating categories...")
        cat_map = {}

        for data in DABELO_CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=data["slug"],
                defaults={**data, "brand": "dabelo", "is_active": True},
            )
            cat_map[data["slug"]] = cat
            self.stdout.write(
                f"  {'Created' if created else 'Exists '} [{cat.brand}] {cat.name}"
            )

        for data in MONTEE_CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=data["slug"],
                defaults={**data, "brand": "montee", "is_active": True},
            )
            cat_map[data["slug"]] = cat
            self.stdout.write(
                f"  {'Created' if created else 'Exists '} [{cat.brand}] {cat.name}"
            )

        # ── Products ──────────────────────────────────────────────────────
        self.stdout.write("\nCreating products...")
        for data in PRODUCTS:
            category = cat_map.get(data["category_slug"])
            variations = data.pop("variations", [])
            attributes = data.pop("attributes", [])
            data.pop("category_slug")

            product, created = Product.objects.get_or_create(
                name=data["name"],
                brand=data["brand"],
                defaults={
                    **data,
                    "category": category,
                    "is_active": True,
                    "in_stock": True,
                    "is_quote_only": data.get("is_quote_only", False),
                },
            )

            label = "Created" if created else "Exists "
            self.stdout.write(f"  {label} [{product.brand}] {product.name}")

            if created:
                # Variations
                for i, v in enumerate(variations):
                    ProductVariation.objects.create(
                        product=product,
                        name=v["name"],
                        price=v["price"],
                        in_stock=v.get("in_stock", True),
                        order=v.get("order", i),
                    )

                # Attributes
                for i, a in enumerate(attributes):
                    ProductAttribute.objects.create(
                        product=product,
                        name=a["name"],
                        value=a["value"],
                        order=i,
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {len(PRODUCTS)} products, {len(DABELO_CATEGORIES) + len(MONTEE_CATEGORIES)} categories seeded."
            )
        )
        self.stdout.write("  Run with --clear to reset and re-seed.\n")
