from datetime import timedelta
from time import sleep

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings

from ..exceptions import (
    EmailConfirmationExpired, EmailIsPrimary, EmailNotConfirmed,
)
from ..models import EmailAddress, get_user_primary_email
from ..signals import (
    email_confirmed, unconfirmed_email_created, primary_email_changed,
)


class EmailConfirmationTestCase(TestCase):

    def setUp(self):
        email = 'nobody@important.com'
        self.user = get_user_model().objects.create_user('uname', email=email)

    def test_key_generation(self):
        "Generate a few keys and make sure they're unique"
        generator = EmailAddress.objects.generate_key
        key1 = generator()
        key2 = generator()
        key3 = generator()

        self.assertNotEqual(key1, key2)
        self.assertNotEqual(key2, key3)
        self.assertNotEqual(key1, key3)

    def test_key_length(self):
        "Generate a few keys and compare them length with the settings"
        generator = EmailAddress.objects.generate_key
        for _ in range(3):
            key = generator()
            self.assertEqual(len(key), settings.SIMPLE_EMAIL_CONFIRMATION_KEY_LENGTH)

    def test_create_confirmed(self):
        "Add an unconfirmed email for a User"
        email = 'test@test.test'

        key = self.user.add_confirmed_email(email)

        address = self.user.email_address_set.get(email=email)
        self.assertTrue(address.is_confirmed)
        self.assertEqual(address.key, key)

    def test_error_create_no_user(self):
        email = 'test@test.test'
        with self.assertRaises(ValueError):
            EmailAddress.objects.create_confirmed(email)
        with self.assertRaises(ValueError):
            EmailAddress.objects.create_unconfirmed(email)

    def test_create_unconfirmed(self):
        "Add an unconfirmed email for a User"
        email = 'test@test.test'

        # assert signal fires as expected
        def listener(sender, **kwargs):
            self.assertEqual(sender, self.user)
            self.assertEqual(email, kwargs.get('email'))
        unconfirmed_email_created.connect(listener)

        key = self.user.add_unconfirmed_email(email)

        address = self.user.email_address_set.get(email=email)
        self.assertFalse(address.is_confirmed)
        self.assertEqual(address.confirmed_at, None)
        self.assertEqual(address.key, key)

    def test_reset_confirmation(self):
        "Reset a confirmation key"
        email = 'test@test.test'
        self.user.add_unconfirmed_email(email)
        address = self.user.email_address_set.get(email=email)
        org_key, org_at = address.key, address.set_at
        sleep(0.1)
        self.user.reset_email_confirmation(email)

        address = self.user.email_address_set.get(email=email)
        self.assertNotEqual(address.key, org_key)
        self.assertGreater(address.set_at, org_at)

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

        self.user.confirm_email(self.user.get_confirmation_key())

        self.assertTrue(self.user.is_confirmed)
        self.assertTrue(self.user.confirmed_at)
        self.assertIn(self.user.email, self.user.get_confirmed_emails())
        self.assertNotIn(self.user.email, self.user.get_unconfirmed_emails())

        self.assertNotIn(email1, self.user.get_confirmed_emails())
        self.assertNotIn(email2, self.user.get_confirmed_emails())
        self.assertNotIn(email3, self.user.get_confirmed_emails())
        self.assertIn(email1, self.user.get_unconfirmed_emails())
        self.assertIn(email2, self.user.get_unconfirmed_emails())
        self.assertIn(email3, self.user.get_unconfirmed_emails())

    def test_confirm_previously_confirmed_confirmation(self):
        "Re-confirm an confirmation that was already confirmed"
        email = 't@t.t'
        key = self.user.add_confirmed_email(email)
        at_before = self.user.email_address_set.get(email=email).confirmed_at

        self.user.confirm_email(key)
        at_after = self.user.email_address_set.get(email=email).confirmed_at

        self.assertIn(email, self.user.get_confirmed_emails())
        self.assertEqual(at_after, at_before)

    @override_settings(SIMPLE_EMAIL_CONFIRMATION_PERIOD=timedelta(weeks=1))
    def test_attempt_confirm_expired_confirmation(self):
        "Try to confirm an expired confirmation"
        email = 't@t.t'
        self.user.add_unconfirmed_email(email)
        address = self.user.email_address_set.get(email=email)
        period = settings.SIMPLE_EMAIL_CONFIRMATION_PERIOD
        address.set_at = address.set_at - period * 2
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

    def test_remove_email(self):
        email_unconfirmed = 'unconfirmed@t.t'
        email_confirmed = 'confirmed@t.t'

        self.user.add_unconfirmed_email(email_unconfirmed)
        self.user.add_confirmed_email(email_confirmed)

        self.assertIn(email_confirmed, self.user.get_confirmed_emails())
        self.assertIn(email_unconfirmed, self.user.get_unconfirmed_emails())

        # can't remove the primary
        with self.assertRaises(EmailIsPrimary):
            self.user.remove_email(self.user.email)

        # can remove the unconfirmed
        self.user.remove_email(email_unconfirmed)
        self.assertNotIn(email_unconfirmed, self.user.get_unconfirmed_emails())

        # can remove the confirmed
        self.user.remove_email(email_confirmed)
        self.assertNotIn(email_confirmed, self.user.get_confirmed_emails())


class PrimaryEmailTestCase(TestCase):

    def setUp(self):
        email = 'nobody@important.com'
        self.user = get_user_model().objects.create_user('uname', email=email)

    def test_set_primary_email(self):
        "Set an email to priamry"
        # set up two emails, confirm them post
        email1 = '1@t.t'
        self.user.add_confirmed_email(email1)
        self.user.set_primary_email(email1)

        email2 = '2@t.t'
        self.user.add_confirmed_email(email2)

        # assert signal fires as expected
        def listener(sender, **kwargs):
            self.assertEqual(sender, self.user)
            self.assertEqual(kwargs.get('old_email'), email1)
            self.assertEqual(kwargs.get('new_email'), email2)
        primary_email_changed.connect(listener)

        self.user.set_primary_email(email2)

        self.assertEqual(self.user.get_primary_email(), email2)

    def test_attempt_set_primary_email_to_unowned_email(self):
        "Try to set a primary email to one that doesn't belong to the user"
        other_user = get_user_model().objects.create_user(
            'myname', email='somebody@important.com',
        )
        email = '1@t.t'
        other_user.add_confirmed_email(email)

        with self.assertRaises(EmailNotConfirmed):
            self.user.set_primary_email(email)

    def test_attempt_set_primary_email_to_unconfirmed_email(self):
        "Try to set a primary email to one that hasn't been confirmed"
        email = '1@t.t'
        self.user.add_unconfirmed_email(email)

        with self.assertRaises(EmailNotConfirmed):
            self.user.set_primary_email(email)

    def test_getting_primary_email_with_mixin(self):
        "Try to get the primary email of a user model with the mixin"
        email = get_user_primary_email(self.user)
        self.assertEqual(email, self.user.email)

    def test_getting_primary_email_without_mixin(self):
        "Try to get the primary email of a user model without the mixin"
        model = apps.get_model('myapp', 'UserWithoutMixin')
        other_user = model.objects.create(email='somebody@important.com')
        email = get_user_primary_email(other_user)
        self.assertEqual(email, other_user.email)


class AddEmailIfNotExistsTestCase(TestCase):

    def setUp(self):
        self.email1 = 'e1@go.com'
        self.email2 = 'e2@go.com'
        self.email3 = 'e3@go.com'
        self.email4 = 'e4@go.com'

        # adds this email as an unconfirmed email
        self.user = get_user_model().objects.create_user(
            'uname', email=self.email1
        )

    def test_add_new_unconfirmed_email(self):
        result = self.user.add_email_if_not_exists(self.email2)

        self.assertEqual(self.user.email_address_set.count(), 2)
        address = self.user.email_address_set.get(key=result)
        self.assertEqual(address.email, self.email2)
        self.assertEqual(address.is_confirmed, False)

    def test_add_old_unconfirmed_email(self):
        self.user.add_unconfirmed_email(self.email2)
        self.user.add_unconfirmed_email(self.email3)

        address = self.user.email_address_set.get(email=self.email2)
        org_key, org_at = address.key, address.set_at

        sleep(0.1)
        result = self.user.add_email_if_not_exists(self.email2)

        self.assertEqual(self.user.email_address_set.count(), 3)
        address = self.user.email_address_set.get(key=result)
        self.assertEqual(address.email, self.email2)
        self.assertEqual(address.is_confirmed, False)
        self.assertNotEqual(address.key, org_key)
        self.assertGreater(address.set_at, org_at)

    def test_add_confirmed_email(self):
        self.user.add_confirmed_email(self.email2)
        self.user.add_confirmed_email(self.email3)

        result = self.user.add_email_if_not_exists(self.email2)

        self.assertIsNone(result)
        self.assertEqual(self.user.email_address_set.count(), 3)
        address = self.user.email_address_set.get(email=self.email2)
        self.assertEqual(address.is_confirmed, True)


class AutoAddTestCase(TestCase):

    def setUp(self):
        self.email = 'nobody@important.com'

    def test_email_is_added_if_not_empty(self):
        user = get_user_model().objects.create_user(
            'uname', email=self.email
        )
        self.assertEqual(user.email_address_set.count(), 1)

        email_address = user.email_address_set.first()
        self.assertFalse(email_address.is_confirmed)
        self.assertEqual(email_address.email, self.email)

    def test_email_is_not_added_if_empty(self):
        user = get_user_model().objects.create_user(
            'uname'
        )
        self.assertEqual(user.email_address_set.count(), 0)
        self.assertFalse(user.is_confirmed)
