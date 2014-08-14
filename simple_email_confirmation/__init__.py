__version__ = '0.11'

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from .models import SimpleEmailConfirmationUserMixin, EmailAddress # NOQA
from .signals import ( # NOQA
    email_confirmed, unconfirmed_email_created, primary_email_changed,
)

# Django 1.7.x compatibility
if hasattr(django, 'setup'):
    django.setup()

# by default, auto-add unconfirmed EmailAddress objects for new Users
if getattr(settings, 'SIMPLE_EMAIL_CONFIRMATION_AUTO_ADD', True):
    def auto_add(sender, **kwargs):
        if sender == get_user_model() and kwargs['created']:
            user = kwargs.get('instance')
            email = user.get_primary_email()
            user.add_unconfirmed_email(email)

    # TODO: try to only connect this to the User model. We can't use
    #       get_user_model() here - results in import loop.

    post_save.connect(auto_add, sender=get_user_model())
