from django.dispatch import Signal

email_confirmed = Signal()  # args: ['user', 'email']
unconfirmed_email_created = Signal()  # args: ['user', 'email']
primary_email_changed = Signal()  # args: ['user', 'old_email', 'new_email']
