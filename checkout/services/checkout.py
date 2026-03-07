from __future__ import annotations

from cart.service import get_or_create_cart


class CheckoutService:
    @staticmethod
    def get_valid_cart(request):
        cart = get_or_create_cart(request)
        items = list(cart.items.select_related("product", "variation"))
        if not items:
            return None, "Your cart is empty."
        return cart, None

    @staticmethod
    def validate_address(post) -> tuple[dict, dict]:
        fields = {
            "name": post.get("name", "").strip(),
            "phone": post.get("phone", "").strip(),
            "line1": post.get("address_line_1", "").strip(),
            "line2": post.get("address_line_2", "").strip(),
            "city": post.get("city", "").strip(),
            "state": post.get("state", "").strip(),
            "notes": post.get("notes", "").strip(),
        }
        required = {
            "name": "Full name is required.",
            "phone": "Phone number is required.",
            "line1": "Address is required.",
            "city": "City is required.",
            "state": "State is required.",
        }
        errors = {key: msg for key, msg in required.items() if not fields[key]}
        return fields, errors
