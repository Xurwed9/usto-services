from django.urls import path
from . import views 

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('confirm-email/', views.confirm_email, name='confirm'),
    path('logout/', views.logout_user, name='logout'),
    
    path('prfile/', views.my_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'), 

    path('forgot-password/', views.forgot_password_request, name='forgot_password'),
]