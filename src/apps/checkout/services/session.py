from __future__ import annotations

SESSION_KEYS = (
    "checkout_reference",
    "checkout_confirmed_order",
)


class CheckoutSessionService:
    @staticmethod
    def set_reference(session, reference: str) -> None:
        session["checkout_reference"] = reference

    @staticmethod
    def get_reference(session) -> str | None:
        return session.get("checkout_reference")

    @staticmethod
    def set_confirmed_order(session, order_number: str) -> None:
        session["checkout_confirmed_order"] = order_number

    @staticmethod
    def get_confirmed_order(session) -> str | None:
        return session.get("checkout_confirmed_order")

    @staticmethod
    def clear(session) -> None:
        for key in SESSION_KEYS:
            session.pop(key, None)
