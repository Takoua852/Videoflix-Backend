from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

LOGO_PATH = Path(settings.BASE_DIR) / "static" / "email" / "logo_icon.png"


def send_html_email(
    *,
    subject: str,
    to_email: str,
    context: dict,
    text_template: str,
    html_template: str,
):
    """
    Sends an HTML email with a plain-text fallback and an inline logo image.
   """
    text_content = render_to_string(text_template, context)
    html_content = render_to_string(html_template, context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = "related"

    try:
        with open(LOGO_PATH, "rb") as f:
            img = MIMEImage(f.read(), _subtype="png")
            img.add_header("Content-ID", "<logo_id>")
            img.add_header(
                "Content-Disposition",
                "inline",
                filename="logo_icon.png",
            )
            msg.attach(img)

        msg.send(fail_silently=False)

    except Exception as exc:
        logger.exception("Email sending failed")
        raise exc


def send_activation_email(email: str, activation_link: str):

    """
    Sends an account activation email with an activation link.
    """
    send_html_email(
        subject="Confirm your email",
        to_email=email,
        context={
            "username": email,
            "activation_link": activation_link,
        },
        text_template="confirm_email.txt",
        html_template="confirm_email.html",
    )


def send_password_reset_email(email: str, reset_link: str):
    
    """
    Sends a password reset email with a reset link.
   """
    send_html_email(
        subject="Reset your password",
        to_email=email,
        context={
            "username": email,
            "reset_link": reset_link,
        },
        text_template="password_email.txt",
        html_template="password_email.html",
    )
