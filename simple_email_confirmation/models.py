from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from .exceptions import (
    EmailConfirmationExpired, EmailIsPrimary, EmailNotConfirmed,
)
from .signals import (
    email_confirmed, unconfirmed_email_created, primary_email_changed,
)


class SimpleEmailConfirmationUserMixin(object):
    """
    Mixin to be used with your django 1.5+ custom User model.
    Provides python-level functionality only.
    """

    # if your User object stores the User's primary email address
    # in a place other than User.email, you can override the
    # primary_email_field_name and/or primary_email get/set methods.
    # All access to a User's primary_email in this app passes through
    # these two get/set methods.

    primary_email_field_name = 'email'

    def get_primary_email(self):
        return getattr(self, self.primary_email_field_name)

    def set_primary_email(self, email, require_confirmed=True):
        "Set an email address as primary"
        old_email = self.get_primary_email()
        if email == old_email:
            return

        if email not in self.confirmed_emails and require_confirmed:
            raise EmailNotConfirmed()

        setattr(self, self.primary_email_field_name, email)
        self.save(update_fields=[self.primary_email_field_name])
        primary_email_changed.send(
            sender=self, old_email=old_email, new_email=email,
        )

    @property
    def is_confirmed(self):
        "Is the User's primary email address confirmed?"
        return self.get_primary_email() in self.confirmed_emails

    @property
    def confirmation_key(self):
        "Confirmation key for the User's primary email"
        email = self.get_primary_email()
        return self.get_confirmation_key(email)

    def get_confirmation_key(self, email):
        "Get the confirmation key for an email"
        address = self.email_address_set.get(email=email)
        return address.key

    @property
    def confirmed_emails(self):
        "List of emails this User has confirmed"
        address_qs = self.email_address_set.filter(confirmed_at__isnull=False)
        return [address.email for address in address_qs]

    @property
    def unconfirmed_emails(self):
        "List of emails this User has been associated with but not confirmed"
        address_qs = self.email_address_set.filter(confirmed_at__isnull=True)
        return [address.email for address in address_qs]

    def confirm_email(self, confirmation_key, save=True):
        "Attempt to confirm an email using the given key"
        self.email_address_set.confirm(confirmation_key, save=save)

    def add_unconfirmed_email(self, email):
        "Adds an unconfirmed email address and returns it's confirmation key"
        # if email already exists, let exception be thrown
        address = self.email_address_set.create_unconfirmed(email)
        return address.key

    def reset_email_confirmation(self, email):
        "Reset the expiration of an email confirmation"
        address = self.email_address_set.get(email=email)
        address.reset_confirmation()

    def remove_email(self, email):
        "Remove an email address and returns it's confirmation key"
        # if email already exists, let exception be thrown
        if email == self.get_primary_email():
            raise EmailIsPrimary()
        address = self.email_address_set.get(email=email)
        address.delete()


class EmailAddressManager(models.Manager):

    def generate_key(self):
        "Generate a new random key and return it"
        # sticking with the django defaults
        return get_random_string()

    def create_unconfirmed(self, email, user=None):
        "Create an email confirmation obj from the given email address obj"
        user = user or self.instance
        if not user:
            raise ValueError('Must specify user or call from related manager')
        key = self.generate_key()
        # let email-already-exists exception propogate through
        address = self.create(user=user, email=email, key=key)
        unconfirmed_email_created.send(sender=user, email=email)
        return address

    def confirm(self, key, user=None, save=True):
        "Confirm an email address"
        queryset = self.all()
        if user:
            queryset = queryset.filter(user=user)
        address = queryset.get(key=key)

        if address.is_key_expired:
            raise EmailConfirmationExpired()

        if not address.is_confirmed:
            address.confirmed_at = now()
            if save:
                address.save(update_fields=['confirmed_at'])
                email_confirmed.send(sender=address.user, email=address.email)

        return address.user


class EmailAddress(models.Model):
    "An email address belonging to a User"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='email_address_set',
    )
    email = models.EmailField(max_length=255)
    key = models.CharField(max_length=40, unique=True)

    set_at = models.DateTimeField(
        default=lambda: now(),
        help_text='When the confirmation key expiration was set',
    )
    confirmed_at = models.DateTimeField(
        blank=True, null=True,
        help_text='First time this email was confirmed',
    )

    objects = EmailAddressManager()

    class Meta:
        unique_together = (('user', 'email'),)

    def __unicode__(self):
        return '{} ({})'.format(self.email, self.user)

    @property
    def is_confirmed(self):
        return self.confirmed_at is not None

    @property
    def is_primary(self):
        return bool(self.user.email == self.email)

    @property
    def key_expires_at(self):
        # By default, keys don't expire. If you want them to, set
        # settings.SIMPLE_EMAIL_CONFIRMATION_PERIOD to a timedelta.
        period = getattr(
            settings, 'SIMPLE_EMAIL_CONFIRMATION_PERIOD', None
        )
        return self.set_at + period if period is not None else None

    @property
    def is_key_expired(self):
        return bool(self.key_expires_at and now() >= self.key_expires_at)

    def reset_confirmation(self):
        """
        Re-generate the confirmation key and key expiration associated
        with this email.  Note that the previou confirmation key will
        cease to work.
        """
        self.key = self._default_manager.generate_key()
        self.set_at = now()
        self.confirmed_at = None
        self.save(update_fields=['key', 'set_at', 'confirmed_at'])


# by default, auto-add unconfirmed EmailAddress objects for new Users
if getattr(settings, 'SIMPLE_EMAIL_CONFIRMATION_AUTO_ADD', True):
    def auto_add(sender, **kwargs):
        if sender == get_user_model() and kwargs['created']:
            user = kwargs.get('instance')
            email = user.get_primary_email()
            user.add_unconfirmed_email(email)

    # TODO: try to only connect this to the User model. We can't use
    #       get_user_model() here - results in import loop.

    post_save.connect(auto_add)
