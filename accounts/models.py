from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class User(AbstractUser):
    role_choice=[
        ('client', 'client'),
        ('master', 'master')
    ]
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=role_choice, default='client')
    phone = models.CharField(max_length=18, blank=True)

    def __str__(self):
        return f"{self.username}--{self.phone if self.phone else 'No Phone'}"
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='users/', blank=True, null=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    
    bio = models.TextField(blank=True, null=True, verbose_name="About Master")
    experience = models.PositiveIntegerField(default=0, verbose_name="Experience in years")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0, verbose_name="Rating")

    def __str__(self):
        return f"Profile of {self.user.username}"
    

class EmailConfirm(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=2)

    def __str__(self):
        return self.user.username