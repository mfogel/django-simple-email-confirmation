from django import newforms as forms
from django.core.validators import alnum_re

from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress

# this code based in-part on django-registration

class SignupForm(forms.Form):
    
    username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput())
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Password (again)", widget=forms.PasswordInput())
    email = forms.EmailField(label="Email (optional)", required=False, widget=forms.TextInput())
    
    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(u"Usernames can only contain letters, numbers and underscores.")
        try:
            user = User.objects.get(username__exact=self.cleaned_data["username"])
        except User.DoesNotExist:
            return self.cleaned_data["username"]
        raise forms.ValidationError(u"This username is already taken. Please choose another.")
    
    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(u"You must type the same password each time.")
        return self.cleaned_data
    
    def save(self):
        print self.cleaned_data
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]
        new_user = User.objects.create_user(username, email, password)
        if email:
            EmailAddress.objects.add_email(new_user, email)
        return username, password # required for authenticate()


class AddEmailForm(forms.Form):
    
    email = forms.EmailField(label="Email", required=True, widget=forms.TextInput())
    
    def save(self, user):
        return EmailAddress.objects.add_email(user, self.cleaned_data["email"])
        