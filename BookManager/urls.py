from django.urls import path
from . import views

app_name = 'BookManager'

urlpatterns = [
	path('', views.home, name = "home"),
]
