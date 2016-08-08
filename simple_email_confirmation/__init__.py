__version__ = '0.21'
__all__ = [
    'email_confirmed',
    'unconfirmed_email_created',
    'primary_email_changed',
]


from .signals import (
    email_confirmed, unconfirmed_email_created, primary_email_changed,
)
