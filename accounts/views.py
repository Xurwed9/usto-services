from django.shortcuts import render, redirect
from .models import EmailConfirm, User
from django.contrib.auth import authenticate, login, logout

# Create your views here.

