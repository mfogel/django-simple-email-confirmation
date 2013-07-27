from django.dispatch import Signal

email_confirmed = Signal(providing_args=['user', 'email'])
unconfirmed_email_created = Signal(providing_args=['user', 'email'])
primary_email_changed = Signal(
    providing_args=['user', 'new_email', 'old_email'],
)
