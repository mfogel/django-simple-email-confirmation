from .exceptions import EmailIsPrimary, EmailNotConfirmed
from .signals import primary_email_changed

from .settings import EmailAddressModel


class SimpleEmailConfirmationUserMixin(object):
    """
    Mixin to be used with your django 1.5+ custom User model.
    Provides python-level functionality only.
    """

    # if your User object stores the User's primary email address
    # in a place other than User.email, you can override the
    # primary_email_field_name and/or primary_email get/set methods.
    # All access to a User's primary_email in this app passes through
    # these two get/set methods.

    primary_email_field_name = 'email'

    def get_primary_email(self):
        return getattr(self, self.primary_email_field_name)

    def set_primary_email(self, email, require_confirmed=True):
        "Set an email address as primary"
        old_email = self.get_primary_email()
        if email == old_email:
            return

        if email not in self.confirmed_emails and require_confirmed:
            raise EmailNotConfirmed()

        setattr(self, self.primary_email_field_name, email)
        self.save(update_fields=[self.primary_email_field_name])
        primary_email_changed.send(
            sender=self, old_email=old_email, new_email=email,
        )

    @property
    def is_confirmed(self):
        "Is the User's primary email address confirmed?"
        return self.get_primary_email() in self.confirmed_emails

    @property
    def confirmed_at(self):
        "When the User's primary email address was confirmed, or None"
        address = self.email_address_set.get(email=self.get_primary_email())
        return address.confirmed_at

    @property
    def confirmation_key(self):
        """
        Confirmation key for the User's primary email

        DEPRECATED. Use get_confirmation_key() instead.
        """
        email = self.get_primary_email()
        return self.get_confirmation_key(email)

    @property
    def confirmed_emails(self):
        "DEPRECATED. Use get_confirmed_emails() instead."
        return self.get_confirmed_emails()

    @property
    def unconfirmed_emails(self):
        "DEPRECATED. Use get_unconfirmed_emails() instead."
        return self.get_unconfirmed_emails()

    def get_confirmation_key(self, email=None):
        "Get the confirmation key for an email"
        email = email or self.get_primary_email()
        address = self.email_address_set.get(email=email)
        return address.key

    def get_confirmed_emails(self):
        "List of emails this User has confirmed"
        address_qs = self.email_address_set.filter(confirmed_at__isnull=False)
        return [address.email for address in address_qs]

    def get_unconfirmed_emails(self):
        "List of emails this User has been associated with but not confirmed"
        address_qs = self.email_address_set.filter(confirmed_at__isnull=True)
        return [address.email for address in address_qs]

    def confirm_email(self, confirmation_key, save=True):
        """
        Attempt to confirm an email using the given key.
        Returns the email that was confirmed, or raise an exception.
        """
        address = self.email_address_set.confirm(confirmation_key, save=save)
        return address.email

    def add_confirmed_email(self, email):
        "Adds an email to the user that's already in the confirmed state"
        # if email already exists, let exception be thrown
        address = self.email_address_set.create_confirmed(email)
        return address.key

    def add_unconfirmed_email(self, email):
        "Adds an unconfirmed email address and returns it's confirmation key"
        # if email already exists, let exception be thrown
        address = self.email_address_set.create_unconfirmed(email)
        return address.key

    def add_email_if_not_exists(self, email):
        """
        If the user already has the email, and it's confirmed, do nothing
        and return None.

        If the user already has the email, and it's unconfirmed, reset the
        confirmation. If the confirmation is unexpired, do nothing. Return
        the confirmation key of the email.
        """
        try:
            address = self.email_address_set.get(email=email)
        except EmailAddressModel.DoesNotExist:
            key = self.add_unconfirmed_email(email)
        else:
            if not address.is_confirmed:
                key = address.reset_confirmation()
            else:
                key = None

        return key

    def reset_email_confirmation(self, email):
        "Reset the expiration of an email confirmation"
        address = self.email_address_set.get(email=email)
        return address.reset_confirmation()

    def remove_email(self, email):
        "Remove an email address"
        # if email already exists, let exception be thrown
        if email == self.get_primary_email():
            raise EmailIsPrimary()
        address = self.email_address_set.get(email=email)
        address.delete()
