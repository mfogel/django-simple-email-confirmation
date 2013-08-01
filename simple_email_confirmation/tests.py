from datetime import timedelta
from time import sleep

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings

from .exceptions import (
    EmailAlreadyConfirmed, EmailConfirmationExpired, EmailUnconfirmed,
)
from .models import EmailAddress
from .signals import (
    email_confirmed, unconfirmed_email_created, primary_email_changed,
)


class EmailConfirmationTestCase(TestCase):

    def setUp(self):
        email = 'nobody@important.com'
        self.user = get_user_model().objects.create_user('uname', email=email)
        self.address = self.user.add_unconfirmed_email(email)

    def test_key_generation(self):
        "Generate a few keys and make sure they're unique"
        generator = EmailAddress.objects.generate_key
        key1 = generator()
        key2 = generator()
        key3 = generator()

        self.assertNotEqual(key1, key2)
        self.assertNotEqual(key2, key3)
        self.assertNotEqual(key1, key3)

    def test_create_unconfirmed(self):
        "Add an unconfirmed email for a User"
        email = 'test@test.test'

        # assert signal fires as expected
        def listener(sender, **kwargs):
            self.assertEqual(sender, self.user)
            self.assertEqual(email, kwargs.get('email'))
        unconfirmed_email_created.connect(listener)

        self.user.add_unconfirmed_email(email)

        address = self.user.email_address_set.get(email=email)
        self.assertFalse(address.is_confirmed)

    def test_reset_confirmation_key(self):
        "Reset a confirmation key"
        email = 'test@test.test'
        address = self.user.add_unconfirmed_email(email)
        org_key, org_at = address.key, address.reset_at
        sleep(0.1)
        address.reset_key()

        self.assertNotEqual(address.key, org_key)
        self.assertGreater(address.reset_at, org_at)

    def test_reset_confirmation_key_expires(self):
        "Reset a confirmation key expiration"
        email = 'test@test.test'
        address = self.user.add_unconfirmed_email(email)
        org_at = address.reset_at
        sleep(0.1)
        address.reset_key_expiration()

        self.assertGreater(address.reset_at, org_at)

    def test_confirm_email(self):
        "Confirm an outstanding confirmation"
        email1, email2, email3 = '1@t.t', '2@t.t', '3@t.t'
        self.user.add_unconfirmed_email(email1)
        self.user.add_unconfirmed_email(email2)
        self.user.add_unconfirmed_email(email3)

        # assert signal fires as expected
        def listener(sender, **kwargs):
            self.assertEqual(sender, self.user)
            self.assertEqual(kwargs.get('email'), self.user.email)
        email_confirmed.connect(listener)

        confirmed_address = self.user.confirm_email(self.address.key)

        self.assertTrue(self.user.is_confirmed)
        self.assertTrue(self.user.is_email_confirmed(self.address.email))
        self.assertEqual(confirmed_address, self.address)
        self.assertFalse(self.user.is_email_confirmed(email1))
        self.assertFalse(self.user.is_email_confirmed(email2))
        self.assertFalse(self.user.is_email_confirmed(email3))

    def test_confirm_previously_confirmed_confirmation(self):
        "Re-confirm an confirmation that was already confirmed"
        email = 't@t.t'
        address = self.user.add_unconfirmed_email(email)
        self.user.confirm_email(address.key)

        with self.assertRaises(EmailAlreadyConfirmed):
            self.user.confirm_email(address.key)

    @override_settings(SIMPLE_EMAIL_CONFIRMATION_PERIOD=timedelta(weeks=1))
    def test_attempt_confirm_expired_confirmation(self):
        "Try to confirm an expired confirmation"
        email = 't@t.t'
        address = self.user.add_unconfirmed_email(email)
        period = settings.SIMPLE_EMAIL_CONFIRMATION_PERIOD
        address.reset_at = address.reset_at - period * 2
        address.save()

        with self.assertRaises(EmailConfirmationExpired):
            self.user.confirm_email(address.key)

    def test_attempt_confirm_invalid_key(self):
        "Try to confirm an with an invalid confirmation key"
        email1, email2 = '1@t.t', '2@t.t'
        self.user.add_unconfirmed_email(email1)
        self.user.add_unconfirmed_email(email2)

        invalid_key = 'thisisnotgoingtoappearrandomaly'
        with self.assertRaises(EmailAddress.DoesNotExist):
            self.user.confirm_email(invalid_key)


class PrimaryEmailTestCase(TestCase):

    def setUp(self):
        email = 'nobody@important.com'
        self.user = get_user_model().objects.create_user('uname', email=email)
        self.address = self.user.add_unconfirmed_email(email)

    def test_set_priamry_email(self):
        "Set an email to priamry"
        # set up two emails, confirm them post
        email1 = '1@t.t'
        address = self.user.add_unconfirmed_email(email1)
        self.user.confirm_email(address.key)
        self.user.set_primary_email(email1)

        email2 = '2@t.t'
        address = self.user.add_unconfirmed_email(email2)
        self.user.confirm_email(address.key)

        # assert signal fires as expected
        def listener(sender, **kwargs):
            self.assertEqual(sender, self.user)
            self.assertEqual(kwargs.get('old_email'), email1)
            self.assertEqual(kwargs.get('new_email'), email2)
        primary_email_changed.connect(listener)

        self.user.set_primary_email(email2)

        self.assertEqual(self.user._get_email(), email2)

    def test_attempt_set_primary_email_to_unowned_email(self):
        "Try to set a primary email to one that doesn't belong to the user"
        other_user = get_user_model().objects.create_user(
            'myname', email='somebody@important.com',
        )
        email = '1@t.t'
        address = other_user.add_unconfirmed_email(email)
        other_user.confirm_email(address.key)

        with self.assertRaises(EmailAddress.DoesNotExist):
            self.user.set_primary_email(email)

    def test_attempt_set_primary_email_to_unconfirmed_email(self):
        "Try to set a primary email to one that hasn't been confirmed"
        email = '1@t.t'
        self.user.add_unconfirmed_email(email)

        with self.assertRaises(EmailUnconfirmed):
            self.user.set_primary_email(email)
