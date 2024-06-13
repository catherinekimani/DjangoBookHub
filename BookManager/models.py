from django.db import models

from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

from django.conf import settings
from cloudinary.models import CloudinaryField
import secrets

from .utils import generate_otp

from django.utils import timezone
from django.conf import settings
# Create your models here.
class CustomUser(AbstractUser):
  email = models.EmailField(unique=True)
  is_verified = models.BooleanField(default=False)
  USERNAME_FIELD = ('email')
  REQUIRED_FIELDS = ["username"]

  def __str__(self):
    return self.email

class OtpToken(models.Model):
		user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otp_tokens')
		otp_code = models.CharField(max_length=6, default=generate_otp, editable=False)
		created = models.DateTimeField(auto_now_add=True)
		expires = models.DateTimeField(blank=True, null=True)

		def __str__(self):
			return self.user.username

class Book(models.Model):
	title = models.CharField(max_length = 100)
	slug = models.SlugField(max_length=100, db_index=True)
	description = models.TextField()
	price = models.IntegerField()
	stock_quantity = models.IntegerField()
	cover_image = CloudinaryField('cover_image')
	book_pages = CloudinaryField('book_pages')
	total_review = models.IntegerField(default=1)
	total_rating = models.IntegerField(default=5)
	status = models.IntegerField(default=0)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = CloudinaryField('profile_pic')
    bio = models.TextField(blank=True)
    favorite_books = models.ManyToManyField(Book, related_name='favorited_by', blank=True)
    purchased_books = models.ManyToManyField(Book, related_name='purchased_by', blank=True)
    books_read = models.ManyToManyField(Book, related_name='read_by', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"