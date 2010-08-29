from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.template.context import RequestContext

from forms import SignupForm, AddEmailForm
from emailconfirmation.models import EmailAddress, EmailConfirmation

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username, password = form.save()
            messages.info(
                request,
                "Confirmation e-mail sent to %s" % form.cleaned_data["email"]
            )
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = SignupForm()
    return render_to_response("signup.html",
        {
            "form": form,
        },
        context_instance=RequestContext(request),
    )

def homepage(request):
    if request.method == "POST" and request.user.is_authenticated():
        if request.POST["action"] == "add":
            add_email_form = AddEmailForm(request.POST, request.user)
            if add_email_form.is_valid():
                add_email_form.save()
                messages.info(
                    request,
                    "Confirmation e-mail sent to %s" % 
                        add_email_form.cleaned_data["email"]
                )
        elif request.POST["action"] == "send":
            email = request.POST["email"]
            try:
                email_address = EmailAddress.objects.get(
                                    user=request.user, email=email
                )
                messages.info(
                    request,
                    "Confirmation e-mail sent to %s" % email
                )
                EmailConfirmation.objects.send_confirmation(email_address)
            except EmailAddress.DoesNotExist:
                pass
            add_email_form = AddEmailForm()
    else:
        add_email_form = AddEmailForm()
    
    return render_to_response("homepage.html",
        {
            "user": request.user,
            "add_email_form": add_email_form,
        },
        context_instance=RequestContext(request),
    )

