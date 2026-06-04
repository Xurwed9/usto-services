from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile 

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.create(user=instance)
        
        try:
            send_mail(
                subject='Хуш омадед ба TajService! 🎉',
                message=f'Салом, {instance.username}! Шумо бо муваффақият дар сайти TajService сабти ном шудед. Акнун метавонед профили худро таҳрир кунед.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email]
            )
            print(f'Email барои корбар {instance.username} фиристода шуд!')
        except Exception as e:
            print(f'Хатогӣ дар фиристодани email: {e}')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()