from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import UserProfile, ReadingNote
import dns.resolver


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Enter a valid email address."
    )

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email already exists
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Please enter a valid email address.")
        
        domain = email.split('@')[1]
        try:
            dns.resolver.resolve(domain, 'MX')
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, Exception):
            raise forms.ValidationError(
                f"The email domain '{domain}' doesn't appear to be valid. "
                "Please check for typos."
            )
        
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = "Letters, digits and @/./+/-/_ only."
        self.fields['password1'].help_text = "At least 8 characters."
        self.fields['password2'].help_text = ""
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Choose a username'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'your@email.com'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm your password'})


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']
        labels = {
            'avatar': 'Profile Picture',
            'bio': 'About You',
        }
        help_texts = {
            'avatar': 'Upload a profile picture (JPG, PNG, or GIF)',
            'bio': 'Share a bit about yourself and your reading interests',
        }
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Tell us about yourself, your favorite books, or reading interests...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })


class ReadingNoteForm(forms.ModelForm):
    """Form for creating and editing reading notes."""
    class Meta:
        model = ReadingNote
        fields = ['note', 'is_public']
        widgets = {
            'note': forms.Textarea(attrs={
                'rows': 6,
                'class': 'form-control',
                'placeholder': 'Write your thoughts about this book...'
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'note': 'Your Note',
            'is_public': 'Share with community',
        }