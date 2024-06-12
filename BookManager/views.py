from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm
from .models import OtpToken
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
# Create your views here.
def home(request):
    return render(request, 'home.html')

"""
function for handling user sign up
"""
def signup(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            messages.success(request, "Account created successfully!! an OTP has been sent to your email")
            return redirect("BookManager:verify_email", username=request.POST['username'])
        else:
            print("Form is not valid:", form.errors)
            context = {'form': form, 'errors': form.errors}
            return render(request, 'signup.html', context)
    context = {'form': form}
    return render(request, 'signup.html', context)

"""
function for handling email verification
"""
def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()
    if request.method == "POST":
        if user_otp.otp_code == request.POST['otp_code']:
            if user_otp.expires > timezone.now():
                user.is_active = True
                user.save()
                storage = messages.get_messages(request)
                storage.used = True
                messages.success(request, "Email verified successfully, you can now login")
                return redirect('BookManager:signin') 
            else:
                messages.warning(request, "OTP has expired, request for another OTP")
                return redirect('BookManager:verify_email', username=user.username)
        else:
            messages.warning(request, "Invalid OTP, try again")
            return redirect('BookManager:verify_email', username=user.username)
    context = {}
    return render(request, 'verify_email.html', context)

"""
function to resend OTP
"""
def resend_otp(request):
    if request.method == "POST":
        user_email = request.POST['email_otp']
        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, expires=timezone.now() + timezone.timedelta(minutes=2))
            subject = "Email Verification"
            message = f"Hello {user.username},\n\nYour OTP is {otp.otp_code} \n it expires in 2 minutes use the url below to verify your email\n\nhttp://127.0.0.1:8000/verify-email/{user.username}"
            sender = settings.EMAIL_HOST_USER
            receiver = [user.email]
            send_mail(subject, message, sender, receiver, fail_silently=False)

            messages.success(request, "A new OTP has been sent to your email")
            return redirect('BookManager:verify_email', username=user.username)
        else:
            messages.error(request, "User does not exist")
            return redirect('BookManager:resend_otp')

    context = {}
    return render(request, 'resend_otp.html', context)
"""
function for handling user sign in
"""
def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Hello {user.username}, you are now logged in")
            return redirect('BookManager:home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('BookManager:signin')
    return render(request, 'signin.html')

"""
function for handling forgot password
"""
def forgot_password(request):
    error_message = None
    success_message = None
    
    if request.method == "POST":
        try:
            user_email = request.POST.get('email')
            if not user_email:
                raise ValidationError("Email field is required")

            if get_user_model().objects.filter(email=user_email).exists():
                user = get_user_model().objects.get(email=user_email)
                otp = OtpToken.objects.create(user=user, expires=timezone.now() + timezone.timedelta(minutes=2))
                subject = "Password Reset"
                message = f"Hello {user.username},\n\nYour OTP is {otp.otp_code} \n it expires in 2 minutes use the url below to reset your password\n\nhttp://127.0.0.1:8000/reset-password/{user.username}"
                sender = settings.EMAIL_HOST_USER
                receiver = [user.email]
                send_mail(subject, message, sender, receiver, fail_silently=False)
                success_message = "Password reset email sent successfully"
                
                return redirect('BookManager:reset_password', username=user.username)
            else:
                raise ValidationError("User with this email does not exist")
        except ValidationError as e:
            error_message = str(e)
        except Exception as e:
            error_message = "unexpected error occurred"
    
    return render(request, 'forgot_password.html', {'error_message': error_message, 'success_message': success_message})

"""
function for handling password reset
"""
def reset_password(request, username):
    if request.method == "POST":
        try:
            user = get_user_model().objects.get(username=username)
            otp_code = request.POST.get('otp_code')
            otp = OtpToken.objects.get(user=user, otp_code=otp_code)
            if otp.expires < timezone.now():
                raise ValidationError("OTP has expired")
            new_password = request.POST.get('new_password')
            print("New Password:", new_password)
            user.set_password(new_password)
            user.save()
            print("Password updated successfully")
            return redirect('BookManager:signin')
        except get_user_model().DoesNotExist:
            error_message = "User not found"
        except OtpToken.DoesNotExist:
            error_message = "Invalid OTP"
        except ValidationError as e:
            error_message = str(e)
        except Exception as e:
            error_message = "An unexpected error occurred"
        return render(request, 'reset_password.html', {'error_message': error_message})

    return render(request, 'reset_password.html', {'username': username})
"""
function handling user signout
"""
def signout(request):
    logout(request)
    return redirect('BookManager:home')


"""
function for handling 404 error
"""
def error_404(request, exception):
    print("Custom 404 handler called")
    return render(request, 'error.html', status=404)