__version__ = '0.13'
__all__ = [
    'SimpleEmailConfirmationUserMixin',
    'EmailAddress',
    'email_confirmed',
    'unconfirmed_email_created',
    'primary_email_changed',
]

import django

from .models import SimpleEmailConfirmationUserMixin, EmailAddress
from .signals import (
    email_confirmed, unconfirmed_email_created, primary_email_changed,
)

if django.get_version() < '4':
    default_app_config = 'simple_email_confirmation.apps.EmailAddress'
