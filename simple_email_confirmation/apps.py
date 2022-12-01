"""Application configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

__all__ = ['EmailAddressConfig']


class EmailAddressConfig(AppConfig):
    """Default configuration for the simple_email_confirmation app."""

    name = 'simple_email_confirmation'
    label = 'simple_email_confirmation'
    verbose_name = _('EmailAddress')
    default_auto_field = 'django.db.models.AutoField'
