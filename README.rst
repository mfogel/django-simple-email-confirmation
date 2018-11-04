django-simple-email-confirmation
================================

.. image:: https://img.shields.io/travis/mfogel/django-simple-email-confirmation/develop.svg
   :target: https://travis-ci.org/mfogel/django-simple-email-confirmation/

.. image:: https://img.shields.io/coveralls/mfogel/django-simple-email-confirmation/develop.svg
   :target: https://coveralls.io/r/mfogel/django-simple-email-confirmation/

.. image:: https://img.shields.io/pypi/dm/django-simple-email-confirmation.svg
   :target: https://pypi.python.org/pypi/django-simple-email-confirmation/

A Django app providing simple email confirmation.

This app can be used to support three different ways of organizing your Users their email address(es). Each email address can be in a confirmed/unconfirmed state.

- Users have one email address that is stored on the `User`
- Users have one primary email address stored on the `User` model, and have N secondary emails stored in `EmailAddress` objects
- Users have N email addresses stored in `EmailAddress` objects.


Examples
--------

Create a new User, confirm their email:

.. code:: python

    from django.core.mail import send_mail
    # ...

    email = 'original@here.com'
    user = User.objects.create_user(email, email=email)
    user.is_confirmed # False

    send_mail(email, 'Use %s to confirm your email' % user.confirmation_key)
    # User gets email, passes the confirmation_key back to your server

    user.confirm_email(user.confirmation_key)
    user.is_confirmed # True

Add another email to an existing User, confirm it, then set it as their primary.

.. code:: python

    new_email = 'newaddr@nowhere.com'
    confirmation_key = user.add_unconfirmed_email(new_email)
    new_email in user.unconfirmed_emails # True

    send_mail(new_email, 'Use %s to confirm your new email' % confirmation_key)
    # User gets email, passes the confirmation_key back to your server

    user.confirm_email(confirmation_key)
    new_email in user.confirmed_emails # True

    user.set_primary_email(new_email)
    user.email # newaddr@nowhere.com


Installation
------------

#.  From `pypi`__ using `pip`__:

    .. code:: sh

        pip install django-simple-email-confirmation

#.  Add `simple_email_confirmation` to your `settings.INSTALLED_APPS`__:

    .. code:: python

        INSTALLED_APPS = (
            ...
            'simple_email_confirmation',
            ...
        )

#.  Add the provided mixin to your `django 1.5+ custom user model`__:

    .. code:: python

        from django.contrib.auth.models import AbstractUser
        from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin

        class User(SimpleEmailConfirmationUserMixin, AbstractUser):
            pass

    Note: you don't strictly have to do this final step. Without this, you won't have the nice helper functions and properties on your `User` objects but the remainder of the app should function fine.

#.  Change default settings (optional):

    By default, keys don't expire. If you want them to, set `settings.SIMPLE_EMAIL_CONFIRMATION_PERIOD` to a timedelta.

    .. code:: python

        from datetime import timedelta

        EMAIL_CONFIRMATION_PERIOD_DAYS = 7
        SIMPLE_EMAIL_CONFIRMATION_PERIOD = timedelta(days=EMAIL_CONFIRMATION_PERIOD_DAYS)

    By default, auto-add unconfirmed EmailAddress objects for new Users. If you want to change this behaviour, set `settings.SIMPLE_EMAIL_CONFIRMATION_AUTO_ADD` to False.

    .. code:: python

        SIMPLE_EMAIL_CONFIRMATION_AUTO_ADD = False

    By default, a length of keys is 12. If you want to change it, set `settings.SIMPLE_EMAIL_CONFIRMATION_KEY_LENGTH` to integer value (maximum 40).

    .. code:: python

        SIMPLE_EMAIL_CONFIRMATION_KEY_LENGTH = 16

    You are able to override the EmailAddress model provided with this app. This works in a similar fashion as Django's custom user model and allows you to add fields to the EmailAddress model, such as a uuid, or define your own model completely. To set a custom email address model, set `settings.SIMPLE_EMAIL_CONFIRMATION_EMAIL_ADDRESS_MODEL` to the model you would like to use in the <app_label>.<model_name> fashion.

    An admin interface is included with simple email confirmation. Although, it is designed to work with the EmailAddress provided. Functionality with the admin cannot be guaranteed when a custom model is used so it is recommended you provide your own admin definition.

    Note for existing apps that already use the provided model:

        Similar to Django's custom user model, migrating a custom email address model after the default one is already migrated is not supported and could have unforeseen side effects. The recommendation is to use a custom model from the beginning of development.

    .. code:: python

        SIMPLE_EMAIL_CONFIRMATION_EMAIL_ADDRESS_MODEL = 'yourapp.EmailAddress'

Python/Django supported versions
--------------------------------

- Python: 2.7, 3.4, 3.5 and 3.6
- Django: 1.8 to 2.0


Running the Tests
-----------------

#.  Install `tox`__ and `coverage`__

    .. code:: sh

        pip install tox coverage

#.  From the repository root, run

    .. code:: sh

        tox
        tox -e coverage

    It's that simple.


Found a Bug?
------------

To file a bug or submit a patch, please head over to `django-simple-email-confirmation on github`__.


Credits
-------

Originally adapted from `Pinax's django-email-confirmation`__, which was originally adapted from `James Tauber's django-email-confirmation`__.


__ http://pypi.python.org/pypi/django-simple-email-confirmation/
__ http://www.pip-installer.org/
__ https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
__ https://docs.djangoproject.com/en/dev/topics/auth/customizing/#specifying-a-custom-user-model
__ https://tox.readthedocs.org/
__ https://coverage.readthedocs.org/
__ https://github.com/mfogel/django-simple-email-confirmation
__ https://github.com/pinax/django-email-confirmation
__ https://github.com/jtauber/django-email-confirmation
