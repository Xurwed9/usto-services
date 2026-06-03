from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('create-services/', views.create_service, name='create_services'),
]