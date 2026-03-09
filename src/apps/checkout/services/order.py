from __future__ import annotations

import logging
import secrets
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.checkout.models import Payment
from apps.products.models import Order, OrderItem

logger = logging.getLogger(__name__)


class OrderService:
    @staticmethod
    def build_order_number() -> str:
        return f"ORD-{secrets.token_hex(4).upper()}"

    @staticmethod
    def payment_already_processed(reference: str) -> bool:
        return Payment.objects.filter(
            reference=reference, status=Payment.Status.SUCCESS
        ).exists()

    @staticmethod
    def get_payment_by_reference(reference: str) -> Payment | None:
        return Payment.objects.filter(reference=reference).first()

    @classmethod
    @transaction.atomic
    def create_pending_order(
        cls,
        *,
        user,
        cart,
        address: dict,
        reference: str,
        total: Decimal,
        subtotal: Decimal,
    ) -> Order:
        address_line = address.get("line1", "")
        if address.get("line2"):
            address_line += f", {address['line2']}"

        order = Order.objects.create(
            user=user,
            order_number=cls.build_order_number(),
            status=Order.Status.PENDING,
            delivery_name=address.get("name", ""),
            delivery_phone=address.get("phone", ""),
            delivery_address=address_line,
            delivery_city=address.get("city", ""),
            delivery_state=address.get("state", ""),
            notes=address.get("notes", ""),
            subtotal=subtotal,
            delivery_fee=Decimal("0"),
            discount=Decimal("0"),
            total=total,
            is_paid=False,
            paystack_ref=reference,
        )

        items = list(cart.items.select_related("product", "variation"))
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=item.product,
                    variation=item.variation,
                    product_name=item.product.name,
                    variation_name=item.variation.name if item.variation else "",
                    product_brand=getattr(item.product, "brand", ""),
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                    line_total=item.line_total,
                )
                for item in items
            ]
        )

        Payment.objects.create(
            order=order,
            user=user,
            reference=reference,
            amount=total,
            status=Payment.Status.PENDING,
        )

        logger.info(
            "Created pending order %s for user %s (ref: %s)",
            order.order_number,
            user.id,
            reference,
        )
        return order

    @classmethod
    @transaction.atomic
    def confirm_order(
        cls,
        *,
        user,
        reference: str,
        paid_amount: Decimal,
        gateway_response: str,
    ) -> Order:
        payment = (
            Payment.objects.select_for_update()
            .filter(reference=reference, user=user)
            .select_related("order")
            .first()
        )

        if not payment:
            logger.warning(
                "confirm_order: no payment found for ref=%s user=%s",
                reference,
                user.id,
            )
            raise ValueError("not_found")

        # Idempotent — webhook may have confirmed it already, just return the order
        if payment.status == Payment.Status.SUCCESS:
            return payment.order

        if paid_amount != payment.amount:
            logger.warning(
                "Amount mismatch ref=%s paid=%s expected=%s user=%s",
                reference,
                paid_amount,
                payment.amount,
                user.id,
            )
            raise ValueError("amount_mismatch")

        cls._mark_success(payment, gateway_response)
        return payment.order

    @classmethod
    @transaction.atomic
    def confirm_order_from_webhook(
        cls,
        *,
        reference: str,
        gateway_response: str,
    ) -> bool:
        payment = (
            Payment.objects.select_for_update()
            .filter(reference=reference)
            .exclude(status=Payment.Status.SUCCESS)
            .select_related("order")
            .first()
        )

        if not payment:
            logger.info("Webhook: already confirmed or not found for ref=%s", reference)
            return False

        cls._mark_success(payment, gateway_response)
        logger.info(
            "Webhook confirmed order %s (ref=%s)",
            payment.order.order_number,
            reference,
        )
        return True

    @staticmethod
    def _mark_success(payment: Payment, gateway_response: str) -> None:
        now = timezone.now()

        payment.status = Payment.Status.SUCCESS
        payment.gateway_response = gateway_response
        payment.paid_at = now
        payment.save(
            update_fields=["status", "gateway_response", "paid_at", "updated_at"]
        )

        order = payment.order
        order.status = Order.Status.CONFIRMED
        order.is_paid = True
        order.paid_at = now
        order.save(update_fields=["status", "is_paid", "paid_at", "updated_at"])
