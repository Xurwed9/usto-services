from django.shortcuts import render, redirect
from .models import EmailConfirm, User, Profile
from django.contrib.auth import authenticate, login, logout
from random import randint
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from services.models import Service
from django.contrib import messages


# Create your views here.

def send_confirmation_email(user):
    code = randint(100000, 999999)
    EmailConfirm.objects.update_or_create(user=user, defaults={'code': code})
    try:
        send_mail(
            subject='Verify your email - TajService',
            message=(
                f'Hello {user.username},\n\n'
                f'Welcome to TajService! Please use the verification code below '
                f'to activate your account:\n\n'
                f'Verification Code: {code}\n\n'
                f'Thank you for joining us!'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,  
        )
        print(f"==================== CODE SENT TO {user.email}: {code} ====================")
    except Exception as e:
        print(f"==================== EMAIL SENDING ERROR: {e} ====================")



def register(request):

    if request.method=="POST":
        username = request.POST.get('username').strip()
        password1 = request.POST.get('password1').strip()
        password2 = request.POST.get('password2').strip()
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone').strip()
        user_role = request.POST.get('role')
        if not username or not email or not password1 or not phone:
            return render(request, 'accounts/register.html', {'error': 'All info are requeired'})
        if password1!=password2:
            return render(request, 'accounts/register.html', {'error': 'Password doesnt match'})
        elif User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already exists'})
        elif User.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {'error': 'Email already exists'})
        elif User.objects.filter(phone=phone).exists():
            return render(request, 'accounts/register.html', {'error': 'Phone already exists'})
        user = User.objects.create_user(username=username, email=email,
                                        password=password1, phone=phone,role=user_role)
        Profile.objects.create(user=user)
        user.is_active=False
        user.save()
        send_confirmation_email(user)
        return render(request,'accounts/confirm_email.html', {'username': user.username})
    else:
        return render(request, 'accounts/register.html')
    


def login_user(request):
    
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if not user:
            not_active = User.objects.filter(username=username, is_active=False).first()
            if not_active:
                return render(request, 'accounts/login.html', {'error':'go and confirm ur email  '})
            else:
                return render(request, 'accounts/login.html', {'error':'Wrong password or username '})
        else:

            login(request, user)
            return redirect('/')
    
    else:
        return render(request, 'accounts/login.html')
    


def logout_user(request):
        logout(request)
        return redirect('login')
    

def confirm_email(request):

    if request.method=='POST':

        username = request.POST.get('username')
        code = request.POST.get('code')

        user = User.objects.filter(username=username).first()
        if not user:
            return render(request, 'accounts/confirm_email.html', {'error': 'Invalid username'})
        
        if user.is_active:
            return redirect('login')
        confirm = EmailConfirm.objects.filter(user=user, code=code).first()

        if not confirm:
            return render(request, 'accounts/confirm_email.html', {'error': 'Wrong code'})
        
        if confirm.is_expired():
            confirm.delete()
            return render(request, 'accounts/confirm_email.html', {
                'error': 'The code has expired. Please register again or request a new code.'
            })
        
        user.is_active= True
        user.save()
        confirm.delete()
        return redirect('login')
    
    else:
        return render(request, 'accounts/confirm_email.html')
    



@login_required
def my_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    my_services = None
    
    if request.user.role == 'master':
        my_services = Service.objects.filter(master=request.user)
        
    context = {
        'my_services': my_services
    }
    return render(request, 'accounts/profile.html', context)




@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile  

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        age = request.POST.get('age')
        city = request.POST.get('city', '').strip()
        
        bio = request.POST.get('bio', '').strip()
        experience = request.POST.get('experience')
        
        photo = request.FILES.get('photo')

        if not username or not email:
            messages.error(request, 'Username and Email are required!')
            return redirect('edit_profile')

        if user.username != username and User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken!')
            return redirect('edit_profile')

        user.username = username
        user.email = email
        user.phone = phone
        if age:
            user.age = int(age)
        user.save()

        profile.city = city
        if photo:
            profile.photo = photo
            
        if user.role == 'master':
            profile.bio = bio
            if experience:
                profile.experience = int(experience)
                
        profile.save()

        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile') 
    return render(request, 'accounts/edit_profile.html')