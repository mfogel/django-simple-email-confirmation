import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin


class User(SimpleEmailConfirmationUserMixin, AbstractUser):
    pass


class UserWithoutMixin(models.Model):
    email = models.EmailField()


class CustomEmailAddress(models.Model):
    """
    A model to test the get_email_address_model method.
    Example of completely overriding the existing email address.
    """
    custom_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    other_field = models.CharField(max_length=255)
