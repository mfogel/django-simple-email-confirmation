__version__ = '0.9'

from .models import SimpleEmailConfirmationUserMixin, EmailAddress      # noqa
from .signals import (                                                  # noqa
    email_confirmed, unconfirmed_email_created, primary_email_changed,
)
