django-simple-email-confirmation
================================

.. image:: https://api.travis-ci.org/mfogel/django-simple-email-confirmation.png?branch=develop
   :target: https://travis-ci.org/mfogel/django-simple-email-confirmation

.. image:: https://coveralls.io/repos/mfogel/django-simple-email-confirmation/badge.png?branch=develop
   :target: https://coveralls.io/r/mfogel/django-simple-email-confirmation

.. image:: https://pypip.in/v/django-simple-email-confirmation/badge.png
   :target: https://crate.io/packages/django-simple-email-confirmation/

.. image:: https://pypip.in/d/django-simple-email-confirmation/badge.png
   :target: https://crate.io/packages/django-simple-email-confirmation/

A Django app providing simple email confirmation.

This app can be used to support three different ways of organizing your Users their email address(es). Each email address can be in a confirmed/unconfirmed state.

- Users have one email address that is stored on the `User`
- Users have one primary email address stored on the `User` model, and have N secondary emails stored in `EmailAddress` objects
- Users have N email addresses stored in `EmailAddress` objects.


Examples
--------

Create a new User, confirm their email:

.. code:: python

    email = 'original@here.com'
    user = User.objects.create_user(email, email=email)
    user.is_confirmed # False

    send_email(email, 'Use %s to confirm your email' % user.confirmation_key)
    # User gets email, passes the confirmation_key back to your server

    user.confirm_email(user.confirmation_key)
    user.is_confirmed # True

Add another email to an existing User, confirm it, then set it as their primary.

.. code:: python

    new_email = 'newaddr@nowhere.com'
    confirmation_key = user.add_unconfirmed_email(new_email)
    new_email in user.unconfirmed_emails # True

    send_email(new_email, 'Use %s to confirm your new email' % confirmation_key)
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
        from simple_email_confirmation import SimpleEmailConfirmationUserMixin

        class User(SimpleEmailConfirmationUserMixin, AbstractUser):
            pass

    Note: you don't strictly have to do this final step. Without this, you won't have the nice helper functions and properties on your `User` objects but the remainder of the app should function fine.


Running the Tests
-----------------

Using `Doug Hellman's virtualenvwrapper`__:

.. code:: sh

    mktmpenv
    pip install django-simple-email-confirmation
    export DJANGO_SETTINGS_MODULE=simple_email_confirmation.test_project.settings
    django-admin.py test simple_email_confirmation


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
__ http://www.doughellmann.com/projects/virtualenvwrapper/
__ https://github.com/mfogel/django-simple-email-confirmation
__ https://github.com/pinax/django-email-confirmation
__ https://github.com/jtauber/django-email-confirmation
