from django.db import models, IntegrityError
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.models import User

# this code based in-part on django-registration

class EmailAddressManager(models.Manager):
    
    def add_email(self, user, email):
        try:
            email_address = self.create(user=user, email=email)
            subject = render_to_string("emailconfirmation/email_confirmation_subject.txt")
            message = render_to_string("emailconfirmation/email_confirmation_message.txt")
            # @@@ eventually use django-mailer
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            print "sent %s '%s' to %s" % (subject, message, email)
            return email_address
        except IntegrityError:
            return None

class EmailAddress(models.Model):
    
    user = models.ForeignKey(User)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    
    objects = EmailAddressManager()
    
    def __unicode__(self):
        return u"%s (%s)" % (self.email, self.user)
    
    class Meta:
        unique_together = (
            ("user", "email"),
        )
    
    class Admin:
        pass
