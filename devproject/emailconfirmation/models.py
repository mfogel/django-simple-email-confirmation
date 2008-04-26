from datetime import datetime, timedelta
from random import random
import sha

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
            EmailConfirmation.objects.send_confirmation(email_address)
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


class EmailConfirmationManager(models.Manager):
    
    def confirm_email(self, confirmation_key):
        try:
            confirmation = self.get(confirmation_key=confirmation_key)
        except self.model.DoesNotExist:
            return None
        if not confirmation.key_expired():
            email_address = confirmation.email_address
            email_address.verified = True
            email_address.save()
            return email_address
    
    def send_confirmation(self, email_address):
        salt = sha.new(str(random())).hexdigest()[:5]
        confirmation_key = sha.new(salt + email_address.email).hexdigest()
        
        subject = render_to_string("emailconfirmation/email_confirmation_subject.txt")
        message = render_to_string("emailconfirmation/email_confirmation_message.txt")
        # @@@ eventually use django-mailer
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email_address.email])
        print "sent %s '%s' to %s" % (subject, message, email_address.email)
        
        return self.create(email_address=email_address, sent=datetime.now(), confirmation_key=confirmation_key)
    
    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmate.delete()

class EmailConfirmation(models.Model):
    
    email_address = models.ForeignKey(EmailAddress, unique=True)
    sent = models.DateTimeField()
    confirmation_key = models.CharField(max_length=40)
    
    objects = EmailConfirmationManager()
    
    def key_expired(self):
        expiration_date = self.sent + timedelta(days=settings.EMAIL_CONFIRMATION_DAYS)
        return expiration_date <= datetime.now()
    key_expired.boolean = True
    
    def __unicode__(self):
        return u"confirmation for %s" % self.email_address
    
    class Admin:
        pass