from django.shortcuts import render, redirect
from .models import EmailConfirm, User, Profile
from django.contrib.auth import authenticate, login, logout
from random import randint
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

def register(request):

    if request.method=="POST":
        username = request.POST.get('username').strip()
        password1 = request.POST.get('password1').strip()
        password2 = request.POST.get('password2').strip()
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone').strip()
        if not username or not email or not password1 or not phone:
            return render(request, 'accounts/register.html', {'error': 'All info are requeired'})
        if password1!=password2:
            return render(request, 'accounts/register.html', {'error': 'Password doesnt match'})
        elif User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already exists'})
        elif User.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {'error': 'Email already exists'})
        elif User.objects.filter(phone=phone).exists():
            return render(request, 'accounts/register.html', {'error': 'Phone already exists'})
        user = User.objects.create_user(username=username, email=email,
                                        password=password1, phone=phone)
        return redirect('login')
    else:
        return render(request, 'accounts/register.html')
    


def login_user(request):
    
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if not user:
            return render(request, 'accounts/login.html' , {"error": 'Username or password is not corect'})
        
        login(request, user)
        print(user.username)
        return redirect('/')
    else:
        return render(request, 'accounts/login.html')