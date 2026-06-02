from django.db import models
from django.contrib.auth.models import AbstractUser

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