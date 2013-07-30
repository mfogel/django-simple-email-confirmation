from django.conf import settings
from django.test import TestCase

from .models import EmailAddress
from .signals import (
    email_confirmed, unconfirmed_email_created, primary_email_changed,
)


class EmailConfirmationTestCase(TestCase):

    def setUp(self):
        # TODO: create a User
        self.user = None

    def test_key_generation(self):
        "Generate a few keys and make sure they're unique"
        generator = EmailAddress.objects.key_generation
        key1 = generator()
        key2 = generator()
        key3 = generator()

        self.assertNotEqual(key1, key2)
        self.assertNotEqual(key2, key3)
        self.assertNotEqual(key1, key3)

    def test_create_unconfirmed(self):
        "Add an unconfirmed email for a User"
        email = 'test@test.test'
        self.user.add_unconfirmed_email(email)

        # assert signal fired
        address = self.user.email_address_set.get(email=email)
        self.assertFalse(address.is_confirmed)

    def test_reset_confirmation_key(self):
        "Reset a confirmation key"
        email = 'test@test.test'
        address = self.user.add_unconfirmed_email(email)
        org_key, org_at = address.key, address.reset_at
        # TODO: sleep?
        sleep(0.1);
        address.reset_key()

        self.assertNotEqual(address.key, org_key)
        self.assertGreater(address.reset_at, org_at)

    def test_reset_confirmation_key_expires(self):
        "Reset a confirmation key expiration"
        email = 'test@test.test'
        address = self.user.add_unconfirmed_email(email)
        org_at = address.reset_at
        # TODO: sleep?
        sleep(0.1);
        address.reset_key_expiration()

        self.assertGreater(address.reset_at, org_at)

    def test_confirm_email(self):
        "Confirm an outstanding confirmation"
        email1, email2, email3 = '1@t.t', '2@t.t', '3@t.t'
        # TODO: silence pylint unused variable?
        address1 = self.user.add_unconfirmed_email(email1)
        address2 = self.user.add_unconfirmed_email(email2)
        address3 = self.user.add_unconfirmed_email(email3)

        self.user.email_address_set.confirm(address2.key)
        # assert the signal fired

        self.assertFalse(self.user.is_confirmed(email1))
        self.assertTrue(self.user.is_confirmed(email2))
        self.assertFalse(self.user.is_confirmed(email3))

    def test_confirm_previously_confirmed_confirmation(self):
        "Re-confirm an confirmation that was already confirmed"
        email = 't@t.t'
        self.user.add_unconfirmed_email(email)
        self.user.email_address_set.confirm(email)

        # assert raises exception
        self.user.email_address_set.confirm(email)

    # settings override
    def test_attempt_confirm_expired_confirmation(self):
        "Try to confirm an expired confirmation"
        email = 't@t.t'
        address = self.user.add_unconfirmed_email(email)
        period = settings.SIMPLE_EMAIL_CONFIRMATION_PERIOD
        # TODO: silence pylint error
        address.reset_at = address.reset_at - period*2

        # assert raises exception
        self.user.email_address_set.confirm(email)

    def test_attempt_confirm_invalid_key(self):
        "Try to confirm an with an invalid confirmation key"
        email1, email2 = '1@t.t', '2@t.t'
        self.user.add_unconfirmed_email(email1)
        self.user.add_unconfirmed_email(email2)

        invalid_key = 'thisisnotgoingtoappearrandomaly'
        # assert raises exception
        self.user.confirm_key(invalid_key)


class PrimaryEmailTestCase(TestCase):

    def setUp(self):
        # TODO: create a User
        self.user = None

    def test_set_priamry_email(self):
        "Set an email to priamry"
        # set up two emails, confirm them post
        email1 = '1@t.t'
        self.user.add_unconfirmed_email(email1)
        self.user.confirm(email1)
        self.user.set_primary_email(email1)

        email2 = '2@t.t'
        self.user.add_unconfirmed_email(email2)
        self.user.confirm(email2)
        self.user.set_primary_email(email2)

        # assert signal fired, twice
        self.assertEqual(self._get_email(), email2)

    def test_attempt_set_primary_email_to_unowned_email(self):
        "Try to set a primary email to one that doesn't belong to the user"
        # TODO: setup another User
        other_user = None
        email = '1@t.t'
        other_user.add_unconfirmed_email(email)
        other_user.confirm(email)

        # assert raises exception
        self.user.set_primary_email(email)

    def test_attempt_set_primary_email_to_unconfirmed_email(self):
        "Try to set a primary email to one that hasn't been confirmed"
        email = '1@t.t'
        self.user.add_unconfirmed_email(email)

        # assert raises exception
        self.set_primary_email(email)
