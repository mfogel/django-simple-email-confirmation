from django import forms            
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import UserCreationForm      


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email')        

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class ConfirmationForm(forms.Form):
    confirmation_key = forms.CharField(required=True)


def index(request):
    return render(request, 'index.html')


def signup(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            send_mail('Email confirmation',
                'Use %s to confirm your email' % user.confirmation_key,
                'example@example.com',
                [user.email])
            login(request, user)
            return redirect('/')
    
    return render(request, 'registration/signup.html', {
        'form': form
    })


def confirm_email(request):
    if request.user.is_confirmed or request.user.is_anonymous:
        return redirect('/')
    form = ConfirmationForm()
    if request.method == "POST" or 'confirmation_key' in request.GET:
        if 'confirmation_key' in request.GET:
            form = ConfirmationForm(data=request.GET)
        else:
            form = ConfirmationForm(data=request.POST)
        if form.is_valid():
            try:
                request.user.confirm_email(form.cleaned_data['confirmation_key'])
            except Exception:
                messages.warning(request, 'Invalid confirmation key')
            if request.user.is_confirmed:
                messages.success(request, 'Email confirmed')
                return redirect('/')
    return render(request, 'registration/confirm_email.html', {
        'form': form
    })