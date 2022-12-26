from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm
from .models import Account

def register(request:HttpRequest):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # email is a unique username; email.split("@")[0] is not unique
            username = email

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()
            messages.success(request, 'Registration was successful')
            return redirect('register_page')

    else: # GET
        form = RegistrationForm()

    context = {
        'registration_form': form
    }
    return render(request, 'accounts/register.html', context)

def login(request:HttpRequest):
    print("Starting login view")
    if request.method == 'POST':
        print("The method is POST")
        email = request.POST['email']
        password = request.POST['password']
        print(f"  email = {email}")
        print(f"  password = {password}")

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            # messages.success(request, 'You are now logged in')
            print("Login succeeded")
            return redirect("home_page")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login_page")

    return render(request, 'accounts/login.html')

# check that the user is logged in, otherwise redirect to the login page
@login_required(login_url = 'login_page')
def logout(request:HttpRequest):
    auth.logout(request)
    messages.success(request, "You are logged out")
    return redirect("login_page")
