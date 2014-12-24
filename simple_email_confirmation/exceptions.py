"Simple Email Confirmation Exceptions"


class SimpleEmailConfirmationException(Exception):
    pass


class EmailNotConfirmed(SimpleEmailConfirmationException):
    pass


class EmailConfirmationExpired(SimpleEmailConfirmationException):
    pass


class EmailIsPrimary(SimpleEmailConfirmationException):
    pass
