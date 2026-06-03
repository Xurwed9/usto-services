from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('create-services/', views.create_service, name='create_services'),
    path('services/<int:id>/', views.service_detail, name='service_detail'),
    path('services/category/<slug:category_slug>/', views.category_services, name='category_services'),
    path('service/update/<int:pk>/', views.update_service, name='update_service'),
    path('service/delete/<int:pk>', views.delete_service, name='delete_service'),
    path('service/toggle/<int:pk>/', views.toggle_service_status, name='toggle_service_status'),
    path('search/', views.service_search, name='service_search'),
]