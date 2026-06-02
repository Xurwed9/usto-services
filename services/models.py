from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")
    slug = models.SlugField(unique=True, verbose_name="URL Slug")
    icon = models.ImageField(upload_to='categories/icons/', blank=True, null=True, verbose_name="Category Icon")

    def __str__(self):
        return self.name
    


class Service(models.Model):
    master = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='services',
        verbose_name="Master / Provider"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='services',
        verbose_name="Category"
    )
    title = models.CharField(max_length=255, verbose_name="Service Title")
    description = models.TextField(verbose_name="Detailed Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Starting Price (TJS)")
    image = models.ImageField(upload_to='services/images/', blank=True, null=True, verbose_name="Service Image")
    
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")


    def __str__(self):
        return f"{self.title} | {self.master.username}"
    



class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('accepted', 'Accepted by Master'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name="Client"
    )
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name="Requested Service"
    )
    description = models.TextField(verbose_name="Problem Description / Order Details")
    address = models.CharField(max_length=255, verbose_name="Delivery Address")
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending', 
        verbose_name="Order Status"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ordered At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")


    def __str__(self):
        return f"Order #{self.id} | {self.client.username} -> {self.status}"
    


class Review(models.Model):
    order = models.OneToOneField(
        Order, 
        on_delete=models.CASCADE, 
        related_name='review',
        verbose_name="Related Order"
    )
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews_written',
        verbose_name="Client"
    )
    master = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews_received',
        verbose_name="Master"
    )
    
    rating = models.PositiveIntegerField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)], 
        verbose_name="Rating Score"
    )
    comment = models.TextField(verbose_name="Review Comment")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Reviewed At")

    def __str__(self):
        return f"Review by {self.client.username} for {self.master.username} ({self.rating}★)"