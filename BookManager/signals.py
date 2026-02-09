from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from .models import OtpToken, UserProfile
from .utils import generate_otp


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_otp_token(sender, instance, created, **kwargs):
    """Create and send OTP token when a new inactive user is created."""
    if created and not instance.is_active:
        otp = OtpToken.objects.create(
            user=instance,
            otp_code=generate_otp(),
            expires=timezone.now() + timezone.timedelta(minutes=2)
        )
        
        subject = "Email Verification"
        message = (
            f"Hello {instance.username},\n\n"
            f"Your OTP is {otp.otp_code}. It expires in 2 minutes. "
            f"Use the URL below to verify your email:\n\n"
            f"http://127.0.0.1:8000/verify_email/{instance.username}"
        )
        sender_email = settings.EMAIL_HOST_USER
        receiver_email = [instance.email]
        
        send_mail(subject, message, sender_email, receiver_email, fail_silently=False)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when a new user is created."""
    if created:
        UserProfile.objects.get_or_create(user=instance)