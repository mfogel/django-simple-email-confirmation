from django.contrib.auth.models import AbstractUser
from simple_email_confirmation import SimpleEmailConfirmationUserMixin


class User(SimpleEmailConfirmationUserMixin, AbstractUser):
    pass
