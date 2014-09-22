__version__ = '0.11'
__all__ = [
    'SimpleEmailConfirmationUserMixin',
    'EmailAddress',
    'email_confirmed',
    'unconfirmed_email_created',
    'primary_email_changed',
]

from .models import SimpleEmailConfirmationUserMixin, EmailAddress
from .signals import (
    email_confirmed, unconfirmed_email_created, primary_email_changed,
)
