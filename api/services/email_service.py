from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import os


def send_confirmition_email(email, confirmation_code):
    subject = 'YamDB activation code'
    email_from = os.getenv('EMAIL_HOST_USER')
    email_to = email
    plain_message = f'Hi, use this code for YamDB login: {confirmation_code}'

    if settings.DEBUG:
        html_message = None
    else:
        context = {
            'email_to': email_to,
            'confirmation_code': confirmation_code
        }
        html_message = render_to_string('confirm-email.html', context=context)

    return send_mail(
        subject,
        plain_message,
        email_from,
        [email_to],
        html_message=html_message,
        fail_silently=False
    )
