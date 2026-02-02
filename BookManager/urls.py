from django.urls import path
from . import views

app_name = 'BookManager'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    
    # Book views
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('toggle-favorite/<int:book_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('toggle-reading-list/<int:book_id>/', views.toggle_reading_list, name='toggle_reading_list'),
    path('toggle-read-status/<int:book_id>/', views.toggle_read_status, name='toggle_read_status'),
    
    # Reading notes
    path('book/<int:book_id>/add-note/', views.add_reading_note, name='add_reading_note'),
    path('note/<int:note_id>/edit/', views.edit_reading_note, name='edit_reading_note'),
    path('note/<int:note_id>/delete/', views.delete_reading_note, name='delete_reading_note'),
    
    # Authentication
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path("verify_email/<slug:username>", views.verify_email, name="verify_email"),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<slug:username>/', views.reset_password, name='reset_password'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('toggle-featured/\u003cint:book_id\u003e/', views.toggle_featured, name='toggle_featured'),
]
