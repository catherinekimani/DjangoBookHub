from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .forms import SignUpForm, UserProfileForm, ReadingNoteForm
from .models import OtpToken, UserProfile, Book, ReadingNote
from .utils import fetch_books


def home(request):
    """Display home page with books from Google Books API."""
    context = {}
    
    if request.user.is_authenticated:
        # Get personalized data for logged-in users
        profile = request.user.profile
        
        # Continue reading: most recent unread book from reading list
        continue_reading_book = profile.reading_list.exclude(
            id__in=profile.books_read.all()
        ).first()
        
        # Fallback to most recent favorite if reading list is empty or all read
        if not continue_reading_book:
            continue_reading_book = profile.favorite_books.first()
        
        # Recent notes (last 4)
        recent_notes = ReadingNote.objects.filter(
            user=request.user
        ).select_related('book').order_by('-created')[:4]
        
        # Reading list count for quick actions
        reading_list_count = profile.reading_list.count()
        
        context.update({
            'continue_reading_book': continue_reading_book,
            'recent_notes': recent_notes,
            'reading_list_count': reading_list_count,
        })
        
        data = fetch_books()
    else:
        data = fetch_books(max_results=9)
    
    books = []
    
    if data and 'items' in data:
        for item in data.get('items', []):
            volume_info = item.get('volumeInfo', {})
            book_id = item.get('id', '')
            
            if not book_id:
                continue
            
            title = volume_info.get('title', 'Unknown')
            authors = ', '.join(volume_info.get('authors', []))
            description = volume_info.get('description', 'No description available')
            published_date = volume_info.get('publishedDate', '')
            page_count = volume_info.get('pageCount')
            categories = ', '.join(volume_info.get('categories', []))
            
            image_links = volume_info.get('imageLinks', {})
            cover_image = (
                image_links.get('extraLarge', '')
                or image_links.get('large', '')
                or image_links.get('medium', '')
                or image_links.get('small', '')
                or image_links.get('thumbnail', '')
                or image_links.get('smallThumbnail', '')
            )
            if cover_image and 'zoom=1' in cover_image:
                cover_image = cover_image.replace('zoom=1', 'zoom=0')
            if cover_image and cover_image.startswith('http://'):
                cover_image = cover_image.replace('http://', 'https://', 1)
            
            # Extract links
            info_link = volume_info.get('infoLink', '')
            preview_link = volume_info.get('previewLink', '')
            
            # Create or get book
            book, created = Book.objects.get_or_create(
                google_books_id=book_id,
                defaults={
                    'title': title,
                    'authors': authors,
                    'description': description,
                    'published_date': published_date,
                    'cover_image': cover_image,
                    'info_link': info_link,
                    'preview_link': preview_link,
                    'page_count': page_count,
                    'categories': categories,
                }
            )
            if cover_image and (not book.cover_image or 'zoom=1' in (book.cover_image or '')):
                book.cover_image = cover_image
                book.save(update_fields=['cover_image'])
            books.append(book)
    
    context['books'] = books
    return render(request, 'home.html', context)

def search(request):
    """Search books from Google Books API and display results."""
    q = request.GET.get('q', '').strip()
    books = []

    if q:
        data = fetch_books(query=q, max_results=24)

        if data and 'items' in data:
            for item in data.get('items', []):
                volume_info = item.get('volumeInfo', {})
                book_id = item.get('id', '')

                if not book_id:
                    continue

                title = volume_info.get('title', 'Unknown')
                authors = ', '.join(volume_info.get('authors', []))
                description = volume_info.get('description', 'No description available')
                published_date = volume_info.get('publishedDate', '')
                page_count = volume_info.get('pageCount')
                categories = ', '.join(volume_info.get('categories', []))

                image_links = volume_info.get('imageLinks', {})
                cover_image = (
                    image_links.get('extraLarge', '')
                    or image_links.get('large', '')
                    or image_links.get('medium', '')
                    or image_links.get('small', '')
                    or image_links.get('thumbnail', '')
                    or image_links.get('smallThumbnail', '')
                )
                if cover_image and 'zoom=1' in cover_image:
                    cover_image = cover_image.replace('zoom=1', 'zoom=0')
                if cover_image and cover_image.startswith('http://'):
                    cover_image = cover_image.replace('http://', 'https://', 1)

                info_link = volume_info.get('infoLink', '')
                preview_link = volume_info.get('previewLink', '')

                book, _created = Book.objects.get_or_create(
                    google_books_id=book_id,
                    defaults={
                        'title': title,
                        'authors': authors,
                        'description': description,
                        'published_date': published_date,
                        'cover_image': cover_image,
                        'info_link': info_link,
                        'preview_link': preview_link,
                        'page_count': page_count,
                        'categories': categories,
                    }
                )
                if cover_image and (not book.cover_image or 'zoom=1' in (book.cover_image or '')):
                    book.cover_image = cover_image
                    book.save(update_fields=['cover_image'])
                books.append(book)

    context = {
        'q': q,
        'books': books,
    }
    return render(request, 'search_results.html', context)


def book_detail(request, book_id):
    """Display detailed information about a book."""
    book = get_object_or_404(Book, id=book_id)
    
    book.view_count += 1
    book.save(update_fields=['view_count'])
    
    preview_embed_url = None
    if book.google_books_id and book.preview_link:
        preview_embed_url = (
            f"https://books.google.com/books"
            f"?id={book.google_books_id}"
            f"&printsec=frontcover"
            f"&output=embed"
        )
    
    user_note = None
    is_favorite = False
    in_reading_list = False
    is_read = False
    user_notes = []
    public_notes = []
    
    if request.user.is_authenticated:
        profile = request.user.profile
        is_favorite = profile.is_book_favorite(book)
        in_reading_list = profile.reading_list.filter(id=book.id).exists()
        is_read = profile.is_book_read(book)
        
        user_notes = ReadingNote.objects.filter(user=request.user, book=book).order_by('-created')
        
        public_notes = ReadingNote.objects.filter(
            book=book,
            is_public=True
        ).exclude(user=request.user).order_by('-created')[:10]
    
    context = {
        'book': book,
        'is_favorite': is_favorite,
        'in_reading_list': in_reading_list,
        'is_read': is_read,
        'user_notes': user_notes,
        'public_notes': public_notes,
        'preview_embed_url': preview_embed_url,
    }
    
    return render(request, 'book_detail.html', context)


@login_required
def toggle_favorite(request, book_id):
    """Toggle favorite status for a book."""
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        profile = request.user.profile
        
        if profile.is_book_favorite(book):
            profile.favorite_books.remove(book)
            is_favorite = False
        else:
            profile.favorite_books.add(book)
            is_favorite = True
        
        return JsonResponse({'is_favorite': is_favorite})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def toggle_reading_list(request, book_id):
    """Toggle reading list status for a book."""
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        profile = request.user.profile
        
        if profile.reading_list.filter(id=book.id).exists():
            profile.reading_list.remove(book)
            in_list = False
        else:
            profile.reading_list.add(book)
            in_list = True
        
        return JsonResponse({'in_reading_list': in_list})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def toggle_read_status(request, book_id):
    """Toggle read status for a book."""
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        profile = request.user.profile
        
        if profile.is_book_read(book):
            profile.books_read.remove(book)
            is_read = False
        else:
            profile.books_read.add(book)
            is_read = True
        
        return JsonResponse({'is_read': is_read})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def add_reading_note(request, book_id):
    """Add a reading note to a book."""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        form = ReadingNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.book = book
            note.save()
            messages.success(request, "Note added successfully!")
            return redirect('BookManager:book_detail', book_id=book.id)
    else:
        form = ReadingNoteForm()
    
    return render(request, 'add_note.html', {'form': form, 'book': book})


@login_required
def edit_reading_note(request, note_id):
    """Edit an existing reading note."""
    note = get_object_or_404(ReadingNote, id=note_id, user=request.user)
    
    if request.method == 'POST':
        form = ReadingNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated successfully!")
            return redirect('BookManager:book_detail', book_id=note.book.id)
    else:
        form = ReadingNoteForm(instance=note)
    
    return render(request, 'edit_note.html', {'form': form, 'note': note, 'book': note.book})


@login_required
def delete_reading_note(request, note_id):
    """Delete a reading note."""
    note = get_object_or_404(ReadingNote, id=note_id, user=request.user)
    book_id = note.book.id
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, "Note deleted successfully!")
        return redirect('BookManager:book_detail', book_id=book_id)
    
    return render(request, 'delete_note.html', {'note': note, 'book': note.book})


@login_required
def profile(request):
    """Display user profile page."""
    user_profile = request.user.profile
    
    notes_count = ReadingNote.objects.filter(user=request.user).count()
    
    from itertools import groupby
    all_notes = ReadingNote.objects.filter(
        user=request.user
    ).select_related('book').order_by('book__title', '-created')
    
    notes_by_book = []
    for book, notes in groupby(all_notes, key=lambda x: x.book):
        notes_by_book.append({
            'book': book,
            'notes': list(notes)
        })
    
    context = {
        'profile': user_profile,
        'favorite_books': user_profile.favorite_books.all(),
        'books_read': user_profile.books_read.all(),
        'reading_list': user_profile.reading_list.all(),
        'notes_count': notes_count,
        'notes_by_book': notes_by_book,
    }
    return render(request, 'profile.html', context)

@login_required
@login_required
def profile_edit(request):
    """Edit user profile."""
    user_profile = request.user.profile
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('BookManager:profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'profile_edit.html', {'form': form})


def signup(request):
    """Handle user registration with auto-login."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to BookHub, {user.username}! Start building your reading list.")
            return redirect("BookManager:home")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = form.fields[field].label or field
                        messages.error(request, f"{field_name}: {error}")
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})

def verify_email(request, username):
    """Handle email verification with OTP."""
    try:
        user = get_user_model().objects.get(username=username)
        user_otp = OtpToken.objects.filter(user=user).last()
        
        if not user_otp:
            messages.error(request, "No OTP found. Please request a new one.")
            return redirect('BookManager:resend_otp')
        
        if request.method == "POST":
            otp_code = request.POST.get('otp_code', '').strip()
            
            if user_otp.otp_code == otp_code:
                if user_otp.expires and user_otp.expires > timezone.now():
                    user.is_active = True
                    user.is_verified = True
                    user.save()
                    messages.success(request, "Email verified successfully! You can now login.")
                    return redirect('BookManager:signin')
                else:
                    messages.warning(request, "OTP has expired. Please request a new OTP.")
                    return redirect('BookManager:resend_otp')
            else:
                messages.warning(request, "Invalid OTP. Please try again.")
        
        return render(request, 'verify_email.html', {'username': username})
    except get_user_model().DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('BookManager:signup')

def resend_otp(request):
    """Resend OTP for email verification."""
    if request.method == "POST":
        user_email = request.POST.get('email_otp', '').strip()
        
        try:
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(
                user=user,
                expires=timezone.now() + timezone.timedelta(minutes=2)
            )
            
            subject = "Email Verification"
            message = (
                f"Hello {user.username},\n\n"
                f"Your OTP is {otp.otp_code}\n"
                f"It expires in 2 minutes. Use the URL below to verify your email:\n\n"
                f"http://127.0.0.1:8000/verify_email/{user.username}"
            )
            sender = settings.EMAIL_HOST_USER
            receiver = [user.email]
            
            send_mail(subject, message, sender, receiver, fail_silently=False)
            messages.success(request, "A new OTP has been sent to your email.")
            return redirect('BookManager:verify_email', username=user.username)
        except get_user_model().DoesNotExist:
            messages.error(request, "User with this email does not exist.")
    
    return render(request, 'resend_otp.html')

def signin(request):
    """Handle user login."""
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, "Please enter both email and password.")
            return render(request, 'signin.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'BookManager:home')
            if next_url.startswith('/'):
                return redirect(next_url)
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    
    return render(request, 'signin.html')

def forgot_password(request):
    """Handle password reset request."""
    if request.method == "POST":
        try:
            user_email = request.POST.get('email', '').strip()
            if not user_email:
                messages.error(request, "Email field is required.")
                return render(request, 'forgot_password.html')
            
            try:
                user = get_user_model().objects.get(email=user_email)
                otp = OtpToken.objects.create(
                    user=user,
                    expires=timezone.now() + timezone.timedelta(minutes=2)
                )
                
                subject = "Password Reset"
                message = (
                    f"Hello {user.username},\n\n"
                    f"Your OTP is {otp.otp_code}\n"
                    f"It expires in 2 minutes. Use the URL below to reset your password:\n\n"
                    f"http://127.0.0.1:8000/reset_password/{user.username}"
                )
                sender = settings.EMAIL_HOST_USER
                receiver = [user.email]
                
                send_mail(subject, message, sender, receiver, fail_silently=False)
                messages.success(request, "Password reset email sent successfully.")
                return redirect('BookManager:reset_password', username=user.username)
            except get_user_model().DoesNotExist:
                messages.error(request, "User with this email does not exist.")
        except Exception as e:
            messages.error(request, "An unexpected error occurred. Please try again.")
    
    return render(request, 'forgot_password.html')

def reset_password(request, username):
    """Handle password reset with OTP verification."""
    try:
        user = get_user_model().objects.get(username=username)
    except get_user_model().DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('BookManager:forgot_password')
    
    if request.method == "POST":
        try:
            otp_code = request.POST.get('otp_code', '').strip()
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            if not otp_code or not new_password:
                messages.error(request, "All fields are required.")
                return render(request, 'reset_password.html', {'username': username})
            
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'reset_password.html', {'username': username})
            
            otp = OtpToken.objects.get(user=user, otp_code=otp_code)
            
            if not otp.expires or otp.expires < timezone.now():
                messages.error(request, "OTP has expired. Please request a new one.")
                return redirect('BookManager:forgot_password')
            
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password has been reset successfully. Please login.")
            return redirect('BookManager:signin')
            
        except OtpToken.DoesNotExist:
            messages.error(request, "Invalid OTP code.")
        except Exception as e:
            messages.error(request, "An unexpected error occurred. Please try again.")
    
    return render(request, 'reset_password.html', {'username': username})

def signout(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, "You've been logged out.")
    return redirect('BookManager:home')


def error_404(request, exception):
    """Handle 404 errors."""
    return render(request, 'error.html', status=404)


@login_required
def admin_dashboard(request):
    """Admin dashboard with stats and quick actions."""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('BookManager:home')
    
    from django.db.models import Count
    
    total_users = get_user_model().objects.count()
    total_books = Book.objects.count()
    total_notes = ReadingNote.objects.count()
    featured_books = Book.objects.filter(is_featured=True).count()
    curated_books = Book.objects.filter(is_curated=True).count()
    
    recent_users = get_user_model().objects.order_by('-date_joined')[:5]
    recent_notes = ReadingNote.objects.select_related('user', 'book').order_by('-created')[:10]
    popular_books = Book.objects.order_by('-view_count')[:10]
    
    suggested_books = Book.objects.filter(
        is_featured=False
    ).order_by('-view_count')[:10]
    
    context = {
        'total_users': total_users,
        'total_books': total_books,
        'total_notes': total_notes,
        'featured_books': featured_books,
        'curated_books': curated_books,
        'recent_users': recent_users,
        'recent_notes': recent_notes,
        'popular_books': popular_books,
        'suggested_books': suggested_books,
    }
    
    return render(request, 'admin_dashboard.html', context)


@login_required
def toggle_featured(request, book_id):
    """Toggle featured status for a book (admin only)."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        book.is_featured = not book.is_featured
        book.save()
        return JsonResponse({'is_featured': book.is_featured})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)