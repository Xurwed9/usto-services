from django.contrib import admin
from .models import User, Profile, EmailConfirm

# Register your models here.

admin.site.register([User, Profile, EmailConfirm])