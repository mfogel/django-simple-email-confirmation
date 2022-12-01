__version__ = '0.13'
__all__ = [
    'email_confirmed',
    'unconfirmed_email_created',
    'primary_email_changed',
]

import django
from django.apps import apps
from django.conf import settings

from .signals import (
    email_confirmed, unconfirmed_email_created, primary_email_changed,
)

if django.get_version() < '4':
    default_app_config = 'simple_email_confirmation.apps.EmailAddressConfig'


def get_email_address_model():
    """Convenience method to return the email model being used."""
    return apps.get_model(getattr(
        settings,
        'SIMPLE_EMAIL_CONFIRMATION_EMAIL_ADDRESS_MODEL',
        'simple_email_confirmation.EmailAddress'
    ))
