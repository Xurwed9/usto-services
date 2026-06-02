from django.contrib import admin
from .models import Category, Service, Order, Review

# Register your models here.

admin.site.register([Category, Service, Order, Review])