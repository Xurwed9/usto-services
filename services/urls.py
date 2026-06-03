from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('create-services/', views.create_service, name='create_services'),
    path('services/<int:id>/', views.service_detail, name='service_detail'),
]