DABELO_BRAND = {
    "name": "Dabelo Café",
    "tagline": "Fresh. Natural. Nourishing.",
    "short_desc": "Premium fresh juices, salads & healthy bowls — no preservatives, no added sugars.",
    "primary_color": "#0F4D2F",
    "accent_color": "#C59A3D",
    "leaf_color": "#7FAF3A",
    "instagram": "#",
    "facebook": "#",
    "twitter": "#",
    "phone": "",
    "email": "",
    "address": "9, Emmanuel Street Irepodun, Shangisha, Magodo",
    "founded": "2025",
}

MOTEE_BRAND = {
    "name": "Motee Cakes",
    "tagline": "Every Slice Tells a Story.",
    "short_desc": "Handcrafted custom cakes for every celebration — baked with love, delivered with elegance.",
    "primary_color": "#E84C9A",
    "accent_color": "#7A4FA3",
    "blue_color": "#1EB1E7",
    "instagram": "#",
    "facebook": "#",
    "twitter": "#",
    "phone": "",
    "email": "",
    "address": "Lagos, Nigeria",
    "founded": "2024",
}


def brand_context(request):
    """Inject both brand configurations into every template."""
    return {
        "dabelo": DABELO_BRAND,
        "motee": MOTEE_BRAND,
    }
