import datetime
import random

from django.conf import settings
from django.db import models
from django.utils.hashcompat import sha_constructor
from django.utils.timezone import now

from .signals import email_confirmed, primary_email_address_changed

try:
    User = settings.AUTH_USER_MODEL
except AttributeError:
    from django.contrib.auth.models import User


class EmailConfirmationExpired(Exception):
    pass


class EmailAddress(models.Model):
    "An email address belonging to a User"

    user = models.ForeignKey(User, related_name='email_address_set')
    email = models.EmailField()
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'email'),)

    @property
    def is_confirmed(self):
        return self.email_confirmation_set.filter(is_confirmed=True).exists()

    def __unicode__(self):
        return u'%s (%s)' % (self.email, self.user)

    def set_primary(self):
        # set all others to is_primary=False
        other_primaries = (
            self.user.email_address_set.filter(is_primary=True)
            .exclude(pk=self.pk)
        )
        for other in other_primaries:
            other.is_primary = False
            other.save()

        # set ourselves to is_primary=True (if necessary)
        if not self.is_primary:
            self.is_primary = True
            self.save()
            primary_email_address_changed.send(
                sender=self.model, email_address=self,
            )


class EmailConfirmationManager(models.Manager):

    def generate_key(self):
        "Generate a new random key and return it"
        return sha_constructor(str(random.random())).hexdigest()

    def create_emailconfirmation(self, email_address=None):
        "Create an email confirmation obj from the given email address obj"
        email_address = email_address or self.instance
        key = self.generate_key()
        confirmation = self.create(
            email_address=email_address, created_at=now(), key=key,
        )
        return confirmation

    def confirm(self, key, user=None, make_primary=True):
        """
        Confirm an email address.

        If an email was already confirmed, we silently re-confirm
        the email address.
        """
        queryset = self.all()
        if user:
            queryset = queryset.filter(email_address__user=user)
        confirmation = queryset.get(key=key)

        if confirmation.is_key_expired:
            raise EmailConfirmationExpired()

        confirmation.confirmed_at = now()
        confirmation.save()
        email_address = confirmation.email_address
        email_confirmed.send(sender=self.model, email_address=email_address)

        if make_primary:
            email_address.set_primary()
            email_address.save()


class EmailConfirmation(models.Model):
    "The token used to confirm an email address"

    email_address = models.ForeignKey(
        EmailAddress, related_name='email_confirmation_set',
    )
    key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField()
    confirmed_at = models.DateTimeField(
        blank=True, null=True,
        help_text='First time this EmailConfirmation was confirmed',
    )

    objects = EmailConfirmationManager()

    @property
    def is_key_expired(self):
        # by default, confirmations don't expire.
        # You can set settings.EMAIL_CONFIRMATION_DAYS if you want them to.
        days = getattr(settings, 'EMAIL_CONFIRMATION_DAYS', None)
        if days:
            expiration = self.created_at + datetime.timedelta(days=days)
            return expiration <= now()
        return False

    def __unicode__(self):
        return u'Confirmation for %s' % self.email_address
