"Simple Email Confirmation Exceptions"


class SimpleEmailConfirmationException(Exception):
    pass

class EmailAlreadyConfirmed(SimpleEmailConfirmationException):
    pass

class EmailNotConfirmed(SimpleEmailConfirmationException):
    pass

class EmailConfirmationExpired(SimpleEmailConfirmationException):
    pass

class EmailIsPrimary(SimpleEmailConfirmationException):
    pass
