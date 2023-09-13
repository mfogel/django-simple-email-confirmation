import django
from django.dispatch import Signal

if django.VERSION < (4, 0):

    email_confirmed = Signal(providing_args=['user', 'email'])
    unconfirmed_email_created = Signal(providing_args=['user', 'email'])
    primary_email_changed = Signal(
        providing_args=['user', 'old_email', 'new_email'],
    )

else:

    email_confirmed = Signal()
    unconfirmed_email_created = Signal()
    primary_email_changed = Signal()
