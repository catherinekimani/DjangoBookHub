import { getCookie } from './utils.js';

export function initializeFavoriteToggles() {
    const csrftoken = getCookie('csrftoken');
    const favoriteButtons = document.querySelectorAll('.toggle-favorite');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.dataset.bookId;
            fetch(`/toggle-favorite/${bookId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                const icon = this.querySelector('.favorite-icon');
                if (data.is_favorite) {
                    icon.textContent = '♥';
                    this.classList.add('active');
                    if (this.innerHTML.includes('Add to Favorites')) {
                        this.innerHTML = '<span class="favorite-icon">♥</span> Remove from Favorites';
                    }
                } else {
                    icon.textContent = '♡';
                    this.classList.remove('active');
                    if (this.innerHTML.includes('Remove from Favorites')) {
                        this.innerHTML = '<span class="favorite-icon">♡</span> Add to Favorites';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
}

export function initializeReadingListToggles() {
    const csrftoken = getCookie('csrftoken');
    const readingListButtons = document.querySelectorAll('.toggle-reading-list');
    
    readingListButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.dataset.bookId;
            fetch(`/toggle-reading-list/${bookId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.in_reading_list) {
                    this.innerHTML = '<i class="fas fa-bookmark"></i> Remove from Reading List';
                } else {
                    this.innerHTML = '<i class="fas fa-bookmark"></i> Add to Reading List';
                    if (window.location.pathname.includes('/profile')) {
                        location.reload();
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
}

export function initializeReadStatusToggles() {
    const csrftoken = getCookie('csrftoken');
    const readStatusButtons = document.querySelectorAll('.toggle-read-status, .toggle-read');
    
    readStatusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.dataset.bookId;
            fetch(`/toggle-read-status/${bookId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_read) {
                    this.innerHTML = '<i class="fas fa-check"></i> Mark as Unread';
                    if (window.location.pathname.includes('/profile')) {
                        location.reload();
                    }
                } else {
                    this.innerHTML = '<i class="fas fa-check"></i> Mark as Read';
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
}

export function initializeFeaturedToggles() {
    const csrftoken = getCookie('csrftoken');
    const featuredButtons = document.querySelectorAll('.toggle-featured-detail');
    
    featuredButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookId = this.dataset.bookId;
            fetch(`/toggle-featured/${bookId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_featured) {
                    this.innerHTML = '<i class="bi bi-star-fill"></i> Unfeature Book';
                } else {
                    this.innerHTML = '<i class="bi bi-star"></i> Feature Book';
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
}

export function initializeAllBookInteractions() {
    initializeFavoriteToggles();
    initializeReadingListToggles();
    initializeReadStatusToggles();
    initializeFeaturedToggles();
}

document.addEventListener('DOMContentLoaded', initializeAllBookInteractions);
