# DjangoBookHub

A modern Django web application for tracking your reading journey. Manage your book collection, take notes, and discover new books with a beautiful dark mode interface.

## Features

- **Book Management** - Search and save books from Google Books API
- **Reading Notes** - Take private or public notes on books
- **Favorites & Reading Lists** - Organize books you love and want to read
- **Dark Mode** - Beautiful light and dark themes
- **User Profiles** - Customize your profile with avatar and bio
- **Reading Stats** - Track your reading progress
- **Smart Search** - Find books by title, author, or ISBN

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/catherinekimani/DjangoBookHub
   cd DjangoBookHub
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv virtual
   source virtual/bin/activate  # On Windows: virtual\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python3 manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python3 manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python3 manage.py runserver
   ```

7. **Open your browser**
   ```
   http://127.0.0.1:8000
   ```

## Project Structure

```
django-book-hub/
├── BookManager/          # Main app
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── urls.py          # URL routing
│   ├── templates/       # HTML templates
│   └── static/          # CSS and JavaScript
│       ├── css/         # Stylesheets
│       └── js/          # JavaScript modules
├── BookHub/             # Project settings
└── manage.py
```

## Tech Stack

- **Backend**: Django 5.1.4
- **Frontend**: Bootstrap 5, Vanilla JavaScript (ES6 modules)
- **Database**: SQLite (default)
- **API**: Google Books API

## Key Features Explained

### Book Search
Search for books using the Google Books API. Results include cover images, descriptions, and metadata.

### Reading Lists
- **Favorites** - Books you love
- **Reading List** - Books you want to read
- **Books Read** - Track your completed books

### Notes System
Take notes on any book. Notes can be:
- **Private** - Only you can see them
- **Public** - Visible to other users

### Admin Dashboard
Admins can:
- View platform statistics
- Feature popular books
- Monitor user activity

## Development

### Code Organization

CSS and JavaScript are separated into modular files:
- `theme.css` - Theme variables and dark mode
- `components.css` - Reusable UI components
- `utils.js` - Shared utility functions
- `book-interactions.js` - Book toggle functionality

### Running Tests


## License

This project is open source and available under the MIT License.

## Contact

Catherine Kimani - [@catherinekimani](https://github.com/catherinekimani)

Project Link: [https://github.com/catherinekimani/DjangoBookHub](https://github.com/catherinekimani/DjangoBookHub)
