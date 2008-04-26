from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login

from forms import SignupForm, AddEmailForm
from emailconfirmation.models import EmailAddress, EmailConfirmation

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username, password = form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = SignupForm()
    return render_to_response("signup.html", {
        "form": form,
    })

def homepage(request):
    if request.method == "POST" and request.user.is_authenticated():
        if request.POST["action"] == "add":
            add_email_form = AddEmailForm(request.POST, request.user)
            if add_email_form.is_valid():
                add_email_form.save()
        elif request.POST["action"] == "send":
            email = request.POST["email"]
            try:
                email_address = EmailAddress.objects.get(user=request.user, email=email)
                request.user.message_set.create(message="Confirmation email sent to %s" % email)
                EmailConfirmation.objects.send_confirmation(email_address)
            except EmailAddress.DoesNotExist:
                pass
            add_email_form = AddEmailForm()
    else:
        add_email_form = AddEmailForm()
    
    return render_to_response("homepage.html", {
        "user": request.user,
        "messages": request.user.get_and_delete_messages(),
        "add_email_form": add_email_form,
    })

