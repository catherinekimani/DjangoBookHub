from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from .models import CustomUser, OtpToken
from django.core.mail import send_mail
from django.utils import timezone
import secrets

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_otp_token(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        otp_code = secrets.token_hex(3)
        otp = OtpToken.objects.create(user=instance, otp_code=otp_code, expires=timezone.now() + timezone.timedelta(minutes=2))
        
        subject = "Email Verification"
        message = f"Hello {instance.username},\n\nYour OTP is {otp.otp_code}. It expires in 2 minutes. Use the URL below to verify your email:\n\nhttp://127.0.0.1:8000/verify-email/{instance.username}"
        sender_email = settings.EMAIL_HOST_USER
        receiver_email = [instance.email]
        
        send_mail(subject, message, sender_email, receiver_email, fail_silently=False)
        instance.is_active = False
        instance.save()
