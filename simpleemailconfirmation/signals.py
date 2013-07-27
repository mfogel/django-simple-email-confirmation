from django.dispatch import Signal

email_address_confirmed = Signal(providing_args=['email_address'])
primary_email_address_changed = Signal(providing_args=['email_address'])
