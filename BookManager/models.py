from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
# Create your models here.
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