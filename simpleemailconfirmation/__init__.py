__version__ = '0.9'

from .models import EmailAddress, EmailConfirmation
from .signals import email_address_confirmed, primary_email_address_changed
