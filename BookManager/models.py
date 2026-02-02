from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from cloudinary.models import CloudinaryField
from .utils import generate_otp


class CustomUser(AbstractUser):
    """Custom user model with email as username."""
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class OtpToken(models.Model):
    """OTP token for email verification and password reset."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otp_tokens'
    )
    otp_code = models.CharField(max_length=6, default=generate_otp, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.otp_code}"


class Theme(models.Model):
    """Represents a curated theme like Climate, AI, etc."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    tagline = models.CharField(
        max_length=200,
        help_text="Short, compelling hook (e.g., 'Making sense of AI disruption')"
    )
    why_now = models.TextField(
        help_text="Explain why this theme matters right now - contextual, urgent, human"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Emoji or icon class (e.g., 'fa-brain')"
    )
    order = models.IntegerField(default=0, help_text="Display order on homepage")
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Book(models.Model):
    """Book model with support for Google Books API data."""
    # Core fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, db_index=True)
    authors = models.CharField(
        max_length=300,
        blank=True,
        help_text="Comma-separated author names"
    )
    description = models.TextField(blank=True)
    published_date = models.CharField(max_length=50, blank=True)

    # Google Books API fields
    google_books_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Google Books volume ID"
    )
    cover_image = models.URLField(
        blank=True,
        help_text="Google Books thumbnail URL"
    )
    info_link = models.URLField(blank=True, help_text="Link to Google Books page")
    preview_link = models.URLField(
        blank=True,
        help_text="Preview/read link if available"
    )

    # File storage
    local_file = CloudinaryField('book_files', blank=True, null=True)

    # Metadata
    page_count = models.IntegerField(null=True, blank=True)
    categories = models.CharField(
        max_length=300,
        blank=True,
        help_text="Google Books categories"
    )

    # Status & stats
    is_curated = models.BooleanField(
        default=False,
        help_text="Manually reviewed and approved"
    )
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    view_count = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:200]
        super().save(*args, **kwargs)


class BookThemedAssociation(models.Model):
    """Many-to-many through model that connects books to themes with context."""
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='theme_associations'
    )
    theme = models.ForeignKey(
        Theme,
        on_delete=models.CASCADE,
        related_name='book_associations'
    )
    contextual_note = models.TextField(
        help_text="Why is THIS book relevant to THIS theme RIGHT NOW? "
                  "Be specific, human, and insightful."
    )
    curator_pick = models.BooleanField(
        default=False,
        help_text="Highlight as a 'Curator's Pick'"
    )
    order = models.IntegerField(default=0, help_text="Order within the theme")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created']
        unique_together = ['book', 'theme']
        verbose_name = 'Book-Theme Association'
        verbose_name_plural = 'Book-Theme Associations'

    def __str__(self):
        return f"{self.book.title} - {self.theme.name}"


class UserProfile(models.Model):
    """User profile with preferences and reading lists."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = CloudinaryField('profile_pic', blank=True, null=True)
    bio = models.TextField(blank=True)
    favorite_books = models.ManyToManyField(
        Book,
        related_name='favorited_by',
        blank=True
    )
    reading_list = models.ManyToManyField(
        Book,
        related_name='on_reading_lists',
        blank=True
    )
    books_read = models.ManyToManyField(
        Book,
        related_name='read_by',
        blank=True
    )
    favorite_themes = models.ManyToManyField(
        Theme,
        related_name='favorited_by_users',
        blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def is_book_favorite(self, book):
        """Check if a book is in favorites."""
        return self.favorite_books.filter(id=book.id).exists()

    def is_book_read(self, book):
        """Check if a book is marked as read."""
        return self.books_read.filter(id=book.id).exists()


class ReadingNote(models.Model):
    """User notes on books."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reading_notes'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='user_notes'
    )
    note = models.TextField()
    is_public = models.BooleanField(
        default=False,
        help_text="Share with community"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Reading Note'
        verbose_name_plural = 'Reading Notes'

    def __str__(self):
        return f"{self.user.username}'s note on {self.book.title}"
