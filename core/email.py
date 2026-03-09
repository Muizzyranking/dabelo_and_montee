import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def send_email(to, subject, body, template=None, context=None):
    """
    Send a branded HTML email with plain text fallback.
    """
    recipients = _resolve_recipients(to)
    if not recipients:
        logger.warning(
            f"send_email called with no valid recipients. Subject: {subject}"
        )
        return False

    ctx = context or {}
    ctx.setdefault("subject", subject)
    ctx.setdefault("body", body)
    ctx.setdefault("site_name", getattr(settings, "SITE_NAME", "Dabelo & Motee"))
    ctx.setdefault(
        "site_url", getattr(settings, "SITE_URL", "https://dabelomontee.com")
    )

    html_template = template or "emails/default.html"
    try:
        html_body = render_to_string(html_template, ctx)
    except Exception as e:
        logger.error(f"Failed to render email template {html_template}: {e}")
        html_body = None

    from_email = getattr(
        settings, "DEFAULT_FROM_EMAIL", "Dabelo & Motee <hello@dabelomontee.com>"
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=recipients,
    )

    if html_body:
        msg.attach_alternative(html_body, "text/html")

    try:
        msg.send()
        logger.info(f"Email sent to {recipients}. Subject: {subject}")
        return True
    except Exception as e:
        logger.error(
            f"Failed to send email to {recipients}. Subject: {subject}. Error: {e}"
        )
        return False


def _resolve_recipients(to):
    """
    Accepts a User, email string, or list of either.
    Returns a flat list of email strings.
    """
    if not isinstance(to, list):
        to = [to]

    emails = []
    for recipient in to:
        if isinstance(recipient, str):
            emails.append(recipient)
        elif hasattr(recipient, "email"):
            if recipient.email:
                emails.append(recipient.email)
    return emails
