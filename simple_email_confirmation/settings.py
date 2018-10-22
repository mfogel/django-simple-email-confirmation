from django.conf import settings
from django.utils.module_loading import import_string


EmailAddressModel = import_string(getattr(
    settings,
    'SIMPLE_EMAIL_CONFIRMATION_EMAIL_ADDRESS_MODEL',
    'simple_email_confirmation.models.EmailAddress',
))
