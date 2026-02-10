import secrets
import requests
import os
from django.conf import settings


def generate_otp():
    """Generate a 6-digit OTP code."""
    return str(secrets.randbelow(10**6)).zfill(6)


def fetch_books(query='science fiction', max_results=10):
    """
    Fetch books from Google Books API.
    
    Args:
        query: Search query string (default: 'science fiction')
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        dict: JSON response from API or None if request fails
    """
    api_key = os.getenv('GOOGLE_BOOKS_API_KEY', settings.GOOGLE_BOOKS_API_KEY)
    url = (
        f"https://www.googleapis.com/books/v1/volumes"
        f"?q={query}&maxResults={max_results}&key={api_key}"
    )
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None