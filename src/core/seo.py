from __future__ import annotations

from dataclasses import dataclass, field

from django.conf import settings

SITE_NAME = getattr(settings, "SITE_NAME", "Dabelo & Motee")
SITE_URL = getattr(settings, "SITE_URL", "https://dabelomontee.com")
DEFAULT_OG = getattr(settings, "DEFAULT_OG_IMAGE", "/static/img/og-default.jpg")
TWITTER_SITE = getattr(settings, "TWITTER_SITE", "@dabelomontee")


@dataclass
class SEOMeta:
    title: str
    description: str
    canonical: str = ""
    og_title: str = ""
    og_description: str = ""
    og_image: str = DEFAULT_OG
    og_type: str = "website"
    twitter_card: str = "summary_large_image"
    twitter_title: str = ""
    twitter_description: str = ""
    twitter_image: str = DEFAULT_OG
    noindex: bool = False
    extra_meta: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.og_title:
            self.og_title = f"{self.title} | {SITE_NAME}"
        if not self.og_description:
            self.og_description = self.description
        if not self.twitter_title:
            self.twitter_title = self.og_title
        if not self.twitter_description:
            self.twitter_description = self.og_description
        if not self.twitter_image:
            self.twitter_image = self.og_image

    @property
    def full_title(self) -> str:
        return f"{self.title} | {SITE_NAME}"


def seo_home() -> SEOMeta:
    return SEOMeta(
        title="Dabelo & Motee — Fresh Food & Bespoke Cakes in Lagos",
        description=(
            "Dabelo Café offers cold-pressed juices, healthy bowls and meal prep in Lagos. "
            "Motee Cakes creates bespoke handcrafted cakes for weddings, birthdays and celebrations."
        ),
        canonical=SITE_URL + "/",
        og_type="website",
    )


def seo_dabelo_home() -> SEOMeta:
    return SEOMeta(
        title="Dabelo Café — Fresh Juices, Bowls & Healthy Food in Lagos",
        description=(
            "Cold-pressed juices, acai bowls, smoothies and healthy meal prep delivered fresh in Lagos. "
            "Order online from Dabelo Café."
        ),
        canonical=SITE_URL + "/dabelo/",
        og_type="website",
    )


def seo_montee_home() -> SEOMeta:
    return SEOMeta(
        title="Motee Cakes — Bespoke Handcrafted Cakes in Lagos",
        description=(
            "Custom celebration cakes for weddings, birthdays, baby showers and corporate events in Lagos. "
            "Order a bespoke cake from Motee Cakes."
        ),
        canonical=SITE_URL + "/montee/",
        og_type="website",
    )


def seo_shop_joint() -> SEOMeta:
    return SEOMeta(
        title="Shop — Dabelo Café & Motee Cakes",
        description=(
            "Browse the full collection from Dabelo Café and Motee Cakes. "
            "Fresh food, juices, and bespoke cakes — all in one place."
        ),
        canonical=SITE_URL + "/shop/",
    )


def seo_shop_dabelo() -> SEOMeta:
    return SEOMeta(
        title="Dabelo Café Shop — Juices, Bowls & Healthy Meals",
        description=(
            "Order cold-pressed juices, acai bowls, smoothies and healthy meal prep online from Dabelo Café Lagos."
        ),
        canonical=SITE_URL + "/shop/dabelo/",
    )


def seo_shop_montee() -> SEOMeta:
    return SEOMeta(
        title="Motee Cakes Shop — Custom Cakes for Every Occasion",
        description=(
            "Browse Motee Cakes' collection of bespoke celebration cakes. "
            "Wedding cakes, birthday cakes and custom creations delivered in Lagos."
        ),
        canonical=SITE_URL + "/shop/montee/",
    )


def seo_category(category) -> SEOMeta:
    brand_name = "Dabelo Café" if category.brand == "dabelo" else "Motee Cakes"
    return SEOMeta(
        title=f"{category.name} — {brand_name}",
        description=(
            category.description
            or f"Browse {category.name} from {brand_name}. Order online in Lagos."
        ),
        canonical=SITE_URL + category.get_absolute_url(),
    )


def seo_product(product) -> SEOMeta:
    brand_name = "Dabelo Café" if product.brand == "dabelo" else "Motee Cakes"

    # Price string for meta
    price_str = ""
    if product.display_price:
        price_str = f" Starting from ₦{product.display_price:,.0f}."
    elif product.is_quote_only:
        price_str = " Price on request."

    description = (
        product.short_description
        or f"{product.name} from {brand_name} in Lagos.{price_str}"
    )

    # OG image — use primary image serve URL if available
    og_image = DEFAULT_OG
    if product.primary_image:
        og_image = SITE_URL + product.primary_image.serve_url

    return SEOMeta(
        title=f"{product.name} — {brand_name}",
        description=description,
        canonical=SITE_URL + product.get_absolute_url(),
        og_type="product",
        og_image=og_image,
        twitter_image=og_image,
        extra_meta={
            "product:brand": brand_name,
            "product:availability": "instock" if product.in_stock else "oos",
            "product:price:amount": str(product.display_price or ""),
            "product:price:currency": "NGN",
        },
    )


def seo_custom_order() -> SEOMeta:
    return SEOMeta(
        title="Custom Orders — Dabelo & Motee",
        description=(
            "Request a custom cake or bespoke food order from Dabelo & Motee. "
            "Submit your brief and our team will get back to you within 24 hours."
        ),
        canonical=SITE_URL + "/custom-order/",
    )


def seo_our_story() -> SEOMeta:
    return SEOMeta(
        title="Our Story — Dabelo & Motee",
        description=(
            "Learn about the story behind Dabelo Café and Motee Cakes — "
            "two Lagos brands built on fresh ingredients, craft and community."
        ),
        canonical=SITE_URL + "/our-story/",
    )
