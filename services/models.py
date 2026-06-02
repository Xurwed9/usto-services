from django.db import models
from django.conf import settings

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")
    slug = models.SlugField(unique=True, verbose_name="URL Slug")
    icon = models.ImageField(upload_to='categories/icons/', blank=True, null=True, verbose_name="Category Icon")

    def __str__(self):
        return self.name