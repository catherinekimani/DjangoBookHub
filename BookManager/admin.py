from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, OtpToken, Theme, Book, 
    BookThemedAssociation, UserProfile, ReadingNote
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser model."""
    list_display = ('email', 'username', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('is_verified', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)


@admin.register(OtpToken)
class OtpTokenAdmin(admin.ModelAdmin):
    """Admin interface for OtpToken model."""
    list_display = ('user', 'otp_code', 'created', 'expires', 'is_expired')
    list_filter = ('created', 'expires')
    search_fields = ('user__email', 'user__username', 'otp_code')
    readonly_fields = ('otp_code', 'created')
    ordering = ('-created',)
    
    def is_expired(self, obj):
        """Check if OTP is expired."""
        from django.utils import timezone
        if obj.expires:
            return obj.expires < timezone.now()
        return False
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """Admin interface for Theme model."""
    list_display = ('name', 'slug', 'tagline', 'order', 'is_active', 'created')
    list_filter = ('is_active', 'created')
    search_fields = ('name', 'tagline')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin interface for Book model."""
    list_display = ('title', 'authors', 'google_books_id', 'is_curated', 'is_featured', 'view_count', 'created')
    list_filter = ('is_curated', 'is_featured', 'created')
    search_fields = ('title', 'authors', 'google_books_id', 'description')
    readonly_fields = ('view_count', 'created', 'updated')
    ordering = ('-created',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'authors', 'description', 'published_date')
        }),
        ('Google Books API', {
            'fields': ('google_books_id', 'cover_image', 'info_link', 'preview_link')
        }),
        ('File Storage', {
            'fields': ('local_file',)
        }),
        ('Metadata', {
            'fields': ('page_count', 'categories')
        }),
        ('Status & Stats', {
            'fields': ('is_curated', 'is_featured', 'view_count')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated')
        }),
    )


@admin.register(BookThemedAssociation)
class BookThemedAssociationAdmin(admin.ModelAdmin):
    """Admin interface for BookThemedAssociation model."""
    list_display = ('book', 'theme', 'curator_pick', 'order', 'created')
    list_filter = ('curator_pick', 'theme', 'created')
    search_fields = ('book__title', 'theme__name', 'contextual_note')
    ordering = ('theme', 'order', '-created')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model."""
    list_display = ('user', 'bio_preview', 'favorite_count', 'reading_list_count', 'created')
    list_filter = ('created', 'updated')
    search_fields = ('user__email', 'user__username', 'bio')
    readonly_fields = ('created', 'updated')
    filter_horizontal = ('favorite_books', 'reading_list', 'books_read', 'favorite_themes')
    
    def bio_preview(self, obj):
        """Show truncated bio."""
        return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = 'Bio'
    
    def favorite_count(self, obj):
        """Count favorite books."""
        return obj.favorite_books.count()
    favorite_count.short_description = 'Favorites'
    
    def reading_list_count(self, obj):
        """Count reading list items."""
        return obj.reading_list.count()
    reading_list_count.short_description = 'Reading List'


@admin.register(ReadingNote)
class ReadingNoteAdmin(admin.ModelAdmin):
    """Admin interface for ReadingNote model."""
    list_display = ('user', 'book', 'note_preview', 'is_public', 'created')
    list_filter = ('is_public', 'created')
    search_fields = ('user__email', 'book__title', 'note')
    readonly_fields = ('created', 'updated')
    ordering = ('-created',)
    
    def note_preview(self, obj):
        """Show truncated note."""
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note'