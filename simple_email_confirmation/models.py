from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .exceptions import EmailConfirmationExpired
from .signals import email_confirmed, unconfirmed_email_created


class EmailAddressManager(models.Manager):

    def generate_key(self):
        "Generate a new random key and return it"
        # By default, a length of keys is 12. If you want to change it, set
        # settings.SIMPLE_EMAIL_CONFIRMATION_KEY_LENGTH to integer value (max 40).
        return get_random_string(
            length=min(getattr(settings, 'SIMPLE_EMAIL_CONFIRMATION_KEY_LENGTH', 12), 40)
        )

    def create_confirmed(self, email, user=None):
        "Create an email address in the confirmed state"
        user = user or getattr(self, 'instance', None)
        if not user:
            raise ValueError('Must specify user or call from related manager')
        key = self.generate_key()
        now = timezone.now()
        # let email-already-exists exception propogate through
        address = self.create(
            user=user, email=email, key=key, set_at=now, confirmed_at=now,
        )
        return address

    def create_unconfirmed(self, email, user=None):
        "Create an email address in the unconfirmed state"
        user = user or getattr(self, 'instance', None)
        if not user:
            raise ValueError('Must specify user or call from related manager')
        key = self.generate_key()
        # let email-already-exists exception propogate through
        address = self.create(user=user, email=email, key=key)
        unconfirmed_email_created.send(sender=user, email=email)
        return address

    def confirm(self, key, user=None, save=True):
        "Confirm an email address. Returns the address that was confirmed."
        queryset = self.all()
        if user:
            queryset = queryset.filter(user=user)
        address = queryset.get(key=key)

        if address.is_key_expired:
            raise EmailConfirmationExpired()

        if not address.is_confirmed:
            address.confirmed_at = timezone.now()
            if save:
                address.save(update_fields=['confirmed_at'])
                email_confirmed.send(sender=address.user, email=address.email)

        return address


def get_user_primary_email(user):
    # softly failing on using these methods on `user` to support
    # not using the SimpleEmailConfirmationMixin in your User model
    # https://github.com/mfogel/django-simple-email-confirmation/pull/3
    if hasattr(user, 'get_primary_email'):
        return user.get_primary_email()
    return user.email


class EmailAddress(models.Model):
    "An email address belonging to a User"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='email_address_set',
        on_delete=models.CASCADE,
    )
    email = models.EmailField(max_length=255)
    key = models.CharField(max_length=40, unique=True)

    set_at = models.DateTimeField(
        default=timezone.now,
        help_text=_('When the confirmation key expiration was set'),
    )
    confirmed_at = models.DateTimeField(
        blank=True, null=True,
        help_text=_('First time this email was confirmed'),
    )

    objects = EmailAddressManager()

    class Meta:
        unique_together = (('user', 'email'),)
        verbose_name_plural = "email addresses"

    def __unicode__(self):
        return '{} <{}>'.format(self.user, self.email)

    @property
    def is_confirmed(self):
        return self.confirmed_at is not None

    @property
    def is_primary(self):
        primary_email = get_user_primary_email(user)
        return bool(primary_email == self.email)

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
        return self.key_expires_at and timezone.now() >= self.key_expires_at

    def reset_confirmation(self):
        """
        Re-generate the confirmation key and key expiration associated
        with this email.  Note that the previou confirmation key will
        cease to work.
        """
        self.key = EmailAddress._default_manager.generate_key()
        self.set_at = timezone.now()

        self.confirmed_at = None
        self.save(update_fields=['key', 'set_at', 'confirmed_at'])
        return self.key


# by default, auto-add unconfirmed EmailAddress objects for new Users
if getattr(settings, 'SIMPLE_EMAIL_CONFIRMATION_AUTO_ADD', True):
    def auto_add(sender, **kwargs):
        if sender == get_user_model() and kwargs['created'] and not kwargs['raw']:
            user = kwargs.get('instance')
            email = get_user_primary_email(user)
            if email:
                if hasattr(user, 'add_unconfirmed_email'):
                    user.add_unconfirmed_email(email)
                else:
                    user.email_address_set.create_unconfirmed(email)

    # TODO: try to only connect this to the User model. We can't use
    #       get_user_model() here - results in import loop.

    post_save.connect(auto_add)
