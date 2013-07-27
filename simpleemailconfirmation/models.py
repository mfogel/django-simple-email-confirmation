import random

from django.conf import settings
from django.db import models
from django.utils.hashcompat import sha_constructor
from django.utils.timezone import now

try:
    # django 1.5+
    User = settings.AUTH_USER_MODEL
except AttributeError:
    # django 1.4
    from django.contrib.auth.models import User

from .signals import (
    email_confirmed, unconfirmed_email_created, primary_email_changed,
)


class EmailConfirmationExpired(Exception):
    pass


class EmailUnconfirmed(Exception):
    pass


class SimpleEmailConfirmationUserMixin(object):
    """
    Mixin to be used with your django 1.5+ custom User model.
    Provides python-level functionality only.
    """

    # override and customize as needed
    email_field_name = 'email'

    def _get_email(self):
        return getattr(self, self.email_field_name)

    def _set_email(self, email):
        setattr(self, self.email_field_name, email)
        # TODO catch django 1.4 update_fields exception and re-save
        self.save(update_fields=[self.email_field_name])

    @property
    def is_email_confirmed(self, email=None):
        """
        Is the email address confirmed for this User?
        Defaults to their primary email.
        """
        if email is None:
            email = getattr(self, self._get_email())
        return (
            self.email_address_set.exclude(confirmed_at__isnull=False)
            .filter(email=email).exists()
        )

    def confirm_email(self, confirmation_key):
        "Attempt to confirm an email using the given key"
        self.email_address_set.confirm(confirmation_key)

    def add_unconfirmed_email(self, email):
        "Adds an unconfirmed email address and returns it"
        # if email already exists, let exception be thrown
        address = self.email_address_set.create_unconfirmed(email)
        return address

    def reset_confirmation_key_expiration(self, email):
        address = self.email_address_set.get(email=email)
        address.reset_key_expiration()

    def set_primary_email(self, email):
        "Set an email address as primary"
        old_email = self._get_email()
        if email == old_email:
            return

        address = self.email_address_set.get(email=email)
        if not address.is_confirmed:
            raise EmailUnconfirmed()

        self._set_email(address.email)
        primary_email_changed.send(self, old_email, self._get_email())


class EmailAddressManager(models.Manager):

    def generate_key(self):
        "Generate a new random key and return it"
        # TODO: a better encoding than hexdigest()?
        # http://docs.python.org/2/library/base64.html ?
        return sha_constructor(str(random.random())).hexdigest()

    def create_unconfirmed(self, email, user=None):
        "Create an email confirmation obj from the given email address obj"
        user = user or self.instance
        if not user:
            raise ValueError('Must specify user or call from related manager')
        key = self.generate_key()
        # let email-already-exists exception propogate through
        address = self.create(user=user, email=email, key=key)
        unconfirmed_email_created.send(user, email)
        return address

    def confirm(self, key, user=None):
        """
        Confirm an email address.

        If an email was already confirmed, we silently re-confirm
        the email address.
        """
        queryset = self.all()
        if user:
            queryset = queryset.filter(user=user)
        email_address = queryset.get(key=key)

        if email_address.is_key_expired:
            raise EmailConfirmationExpired()

        email_address.confirmed_at = now()
        # TODO: catch django 1.4 update_fields exception
        email_address.save(update_fields=['confirmed_at'])
        email_confirmed.send(sender=self.model, email_address=email_address)


class EmailAddress(models.Model):
    "An email address belonging to a User"

    user = models.ForeignKey(User, related_name='email_address_set')
    email = models.EmailField()
    key = models.CharField(max_length=40, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    reset_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Last time the confirmation key expiration was reset',
    )
    confirmed_at = models.DateTimeField(
        blank=True, null=True,
        help_text='First time this email was confirmed',
    )

    objects = EmailAddressManager()

    class Meta:
        unique_together = (('user', 'email'),)

    def __unicode__(self):
        return u'%s (%s)' % (self.email, self.user)

    @property
    def is_confirmed(self):
        return self.confirmed_at is not None

    @property
    def is_primary(self):
        return bool(self.user.email == self.email)

    @property
    def key_expires_at(self):
        # By default, keys don't expire. If you want them to, set
        # settings.SIMPLE_EMAIL_CONFIRMATION_EXPIRATION_PERIOD to a timedelta.
        period = getattr(
            settings, 'SIMPLE_EMAIL_CONFIRMATION_EXPIRATION_PERIOD', None
        )
        return self.reset_at + period if period is not None else None

    @property
    def is_key_expired(self):
        return self.key_expires_at and now() >= self.key_expires_at

    def reset_key_expiration(self):
        self.reset_at = now()
        # TODO: catch django 1.4 exception
        self.save(update_fields=['reset_at'])
