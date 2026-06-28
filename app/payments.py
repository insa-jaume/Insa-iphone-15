"""Integración con Stripe: alta de suscripción (Checkout), portal y webhooks."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import stripe
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Subscription, SubscriptionStatus, User

log = logging.getLogger("payments")

if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key

_STATUS_MAP = {
    "incomplete": SubscriptionStatus.incomplete,
    "incomplete_expired": SubscriptionStatus.canceled,
    "trialing": SubscriptionStatus.trialing,
    "active": SubscriptionStatus.active,
    "past_due": SubscriptionStatus.past_due,
    "canceled": SubscriptionStatus.canceled,
    "unpaid": SubscriptionStatus.unpaid,
}


def ensure_customer(db: Session, user: User) -> str:
    """Crea (o recupera) el cliente de Stripe asociado al usuario."""
    if user.stripe_customer_id:
        return user.stripe_customer_id
    customer = stripe.Customer.create(email=user.email, name=user.full_name or None,
                                      metadata={"user_id": str(user.id)})
    user.stripe_customer_id = customer.id
    db.commit()
    return customer.id


def create_checkout_session(db: Session, user: User) -> str:
    """Devuelve la URL de Stripe Checkout para suscribirse (5 €/mes)."""
    customer_id = ensure_customer(db, user)
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        success_url=f"{settings.site_url}/panel?checkout=ok",
        cancel_url=f"{settings.site_url}/panel?checkout=cancel",
        allow_promotion_codes=True,
        subscription_data={"metadata": {"user_id": str(user.id)}},
    )
    return session.url


def create_billing_portal(db: Session, user: User) -> str:
    """Portal de cliente para gestionar/cancelar la suscripción."""
    customer_id = ensure_customer(db, user)
    portal = stripe.billing_portal.Session.create(
        customer=customer_id, return_url=f"{settings.site_url}/panel"
    )
    return portal.url


def _upsert_subscription(db: Session, user: User, sub_obj: dict) -> None:
    sub = user.subscription or Subscription(user_id=user.id)
    sub.stripe_subscription_id = sub_obj.get("id")
    sub.status = _STATUS_MAP.get(sub_obj.get("status", ""), SubscriptionStatus.incomplete)
    period_end = sub_obj.get("current_period_end")
    if period_end:
        sub.current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc)
    sub.cancel_at_period_end = bool(sub_obj.get("cancel_at_period_end"))
    if user.subscription is None:
        db.add(sub)
    db.commit()


def handle_webhook(db: Session, payload: bytes, sig_header: str) -> str:
    """Procesa un evento de Stripe (verificando la firma). Devuelve el tipo."""
    event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    etype = event["type"]
    obj = event["data"]["object"]

    def _find_user() -> User | None:
        uid = (obj.get("metadata") or {}).get("user_id")
        if uid:
            u = db.get(User, int(uid))
            if u:
                return u
        cust = obj.get("customer")
        if cust:
            return db.scalar(select(User).where(User.stripe_customer_id == cust))
        return None

    if etype in (
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    ):
        user = _find_user()
        if user:
            _upsert_subscription(db, user, obj)
    elif etype == "checkout.session.completed":
        user = _find_user()
        if user and obj.get("subscription"):
            sub_obj = stripe.Subscription.retrieve(obj["subscription"])
            _upsert_subscription(db, user, sub_obj)

    log.info("Webhook Stripe procesado: %s", etype)
    return etype
