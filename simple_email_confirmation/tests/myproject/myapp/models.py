from django.contrib.auth.models import AbstractUser
from django.db import models

from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin


class User(SimpleEmailConfirmationUserMixin, AbstractUser):
    pass


class UserWithoutMixin(models.Model):
       email = models.EmailField()
