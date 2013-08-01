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

This app can be used to support three types of User models:

- Users have one email address that is stored on the `User` model
- Users have one primary email address stored on the `User` model, and have N secondary emails stored in `EmailAddress` objects
- Users have N email addresses stored in `EmailAddress` objects.

Examples
--------

Add the provided mixin to your `django 1.5+ custom user model`__:

.. code:: python

    from django.contrib.auth.models import AbstractUser
    from simple_email_confirmation import SimpleEmailConfirmationUserMixin

    class User(SimpleEmailConfirmationUserMixin, AbstractUser):
        pass

then, when creating a new User you probably want to do something like:

.. code:: python

    user = User.objects.create_user('original@here.com')
    address = user.add_unconfirmed_email(user.email)

    confirmation_key = address.key
    user.is_confirmed # False

    send_email(user.email, 'Use %s to confirm your email' % confirmation_key)
    # User gets email, passes the confirmation_key back to your server

    user.confirm_email(confirmation_key)
    user.is_confirmed # True

when changing a User's email, the flow might go:

.. code:: python

    new_email = 'newaddr@nowhere.com'
    address = user.add_unconfirmed_email(new_email)

    confirmation_key = address.key
    user.is_email_confirmed(new_email) # False

    send_email(new_email, 'Use %s to confirm your new email' % confirmation_key)
    # User gets email, passes the confirmation_key back to your server

    user.confirm_email(confirmation_key)
    user.is_email_confirmed(new_email) # True

    user.set_primary_email(new_email)
    user.email # newaddr@nowhere.com


Installation
------------

From `pypi`__ using `pip`__:

.. code:: sh

    pip install django-timezone-field

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


__ https://docs.djangoproject.com/en/dev/topics/auth/customizing/#specifying-a-custom-user-model
__ http://pypi.python.org/pypi/django-simple-email-confirmation/
__ http://www.pip-installer.org/
__ http://www.doughellmann.com/projects/virtualenvwrapper/
__ https://github.com/mfogel/django-simple-email-confirmation
__ https://github.com/pinax/django-email-confirmation
__ https://github.com/jtauber/django-email-confirmation
