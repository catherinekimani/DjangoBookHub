from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm

# Create your views here.
def home(request):
    return render(request, 'home.html')

"""
function for handling user sign up
"""
def signup(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('BookManager:signin')
    return render(request, 'signup.html', {"form":form})

"""
function for handling user sign in
"""
def signin(request):
    if request.user.is_authenticated:
        return ('BookManager:home')
    else:
        if request.method == "POST":
            user = request.POST.get('user')
            password = request.POST.get('password')

            # try to authenticate user
            auth = authenticate(request, username=user, password=password)
            # if it is successful
            if auth is not None:
                login(request, auth)
                return redirect('BookManager:home')
            else:
                # if it fails
                messages.error(request, "Username and password do not match")
    return render(request, 'signin.html')

"""
function for handling user signout
"""
def signout(request):
    logout(request)
    return redirect('BookManager:home')