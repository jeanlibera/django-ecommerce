from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.exceptions import ObjectDoesNotExist

from .forms import RegistrationForm
from .models import Account
from management.models import Secret

def send_email(subject: str, message: str, recipient_list: list):
    smtp_username_list = Secret.objects.filter(secret_name='smtp-username')
    if len(smtp_username_list) == 0:
        raise ObjectDoesNotExist("Could not find the secret, smtp-username")
    smtp_username = smtp_username_list[0].value
    print(f"smtp_username is {smtp_username}")

    smtp_password_list = Secret.objects.filter(secret_name='smtp-password')
    if len(smtp_password_list) == 0:
        raise ObjectDoesNotExist("Could not find the secret, smtp-password")
    smtp_password = smtp_password_list[0].value
    print(f"smtp_password is {smtp_password}")

    send_mail(subject=subject, message=message, from_email=smtp_username, recipient_list=recipient_list, auth_user=smtp_username, auth_password=smtp_password)
    
    return HttpResponse("Sent an email")

def register(request:HttpRequest):
    if request.method == 'POST':
        print("register is a POST request")
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # email is a unique username; email.split("@")[0] is not unique
            username = email
            print(f"username={username}, email={email}")

            user:Account = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()
            print("Save user succeeded")
            
            # compose the user activation email
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            # the properties are objects that can be used in the html template, 
            # accounts/account_verification_email.html
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                # we are encoding the user id with base64 encoding
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
		        'token': default_token_generator.make_token(user),
            })
            
            send_email(subject=mail_subject, message=message, recipient_list=[email])

            # messages.success(request, 'Thank you for registering with us. We have sent a verification email to {email}.')
            return redirect('/accounts/login/?command=verification&email=' + email)

    else: # GET
        form = RegistrationForm()

    context = {
        'registration_form': form
    }
    return render(request, 'accounts/register.html', context)

def login(request:HttpRequest):
    print("Starting login request handler")
    if request.method == 'POST':
        print("The method is POST")
        email = request.POST['email']
        password = request.POST['password']
        print(f"  email = {email}")
        print(f"  password = {password}")

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            print("Login succeeded")
            messages.success(request, "You are now logged in")
            return redirect("dashboard_page")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login_page")

    return render(request, 'accounts/login.html')

# check that the user is logged in, otherwise redirect to the login page
@login_required(login_url = 'login_page')
def logout(request:HttpRequest):
    print("Starting logout request handler")
    auth.logout(request)
    messages.success(request, "You are logged out")
    return redirect("login_page")

def activate(request:HttpRequest, uidb64, token):
    print(f"Starting logout request handler")
    print(f" uidb64={uidb64}, token={token}")
    try:
        # get the primary key of the user (uid = user id)
        uid = urlsafe_base64_decode(uidb64)
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if (user is not None) and (default_token_generator.check_token(user, token)):
        user.is_active = True
        user.save()
        print(f"Set {user.email} to Active")
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login_page')
    else:
        messages.error('Invalid activation link')
        return redirect('register_page')

@login_required(login_url = 'login_page')
def dashboard(request: HttpRequest):
    return render(request, 'accounts/dashboard.html')

