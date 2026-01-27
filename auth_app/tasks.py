from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


LOGO_URL = "https://takoua-jelassi.developerakademie.net/logo_icon.png"


def send_activation_email_task(email: str, activation_link: str):

    """
    Task for sending account activation email.
    """

    subject = "Confirm your email"
    context = {
        "username": email,
        "activation_link": activation_link,
        "logo_url": LOGO_URL,
    }
    text_content = render_to_string("confirm_email.txt", context)
    html_content = render_to_string("confirm_email.html", context)
    msg = EmailMultiAlternatives(
        subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_password_reset_email_task(email: str, reset_link: str):

    """
    Task for sending password reset email
    """

    subject = "Reset your password"
    context = {
        "username": email,
        "reset_link": reset_link,
        "logo_url": LOGO_URL,
    }
    text_content = render_to_string("password_email.txt", context)
    html_content = render_to_string("password_email.html", context)
    msg = EmailMultiAlternatives(
        subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
