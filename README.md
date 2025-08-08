

## 6. Requirements.txt

```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-WTF==1.1.1
WTForms==3.0.1
Werkzeug==2.3.7
email-validator==2.0.0
python-dotenv==1.0.0
Flask-Migrate==4.0.5
```

## Key Integration Points Explained

### 1. Jinja2 Templating - WHY and WHERE used:

**WHY JINJA2 is used:**
- **Server-side rendering**: Generates HTML on the server with dynamic content
- **Template inheritance**: Reduces code duplication with base templates
- **Security**: Automatic HTML escaping prevents XSS attacks
- **Integration**: Seamless Flask integration with context variables
- **Logic in templates**: Supports conditionals, loops, and filters

**WHERE JINJA2 is used:**
- `{% extends "base.html" %}` - Template inheritance
- `{{ url_for('index') }}` - URL generation for routes
- `{% if current_user.is_authenticated %}` - Conditional rendering
- `{% for post in recent_posts %}` - Loop through database results
- `{{ post.title }}` - Variable rendering with auto-escaping
- `{% with messages = get_flashed_messages() %}` - Message flashing
- `{{ csrf_token() }}` - CSRF protection in forms

### 2. AJAX Concepts - WHY and WHERE used:

**WHY AJAX is used:**
- **Asynchronous communication**: No page reloads for better UX
- **Dynamic content loading**: Load data on demand
- **Form submissions**: Submit forms without page refresh
- **Real-time search**: Instant search results
- **Pagination**: Load more content seamlessly

**WHERE AJAX is used:**
- Search functionality: `POST /api/search` - Real-time search
- Content filtering: `GET /api/posts` - Dynamic post filtering
- Load more posts: Pagination without page reload
- Comment submission: `POST /api/comment` - Add comments asynchronously
- Category/tag filtering: Dynamic content updates

### 3. Form Handling Integration:

- **WTForms**: Server-side validation and CSRF protection
- **AJAX submissions**: Combine form validation with async requests  
- **Error handling**: Display validation errors without page reload
- **File uploads**: Handle file uploads with progress indicators

This complete integration demonstrates how Flask backend services work with your existing frontend, showing the power of combining Jinja2 templating for server-side rendering with AJAX for dynamic client-side interactions.

# Flask Blog Application

A modern, full-featured blog application built with Flask, demonstrating best practices for web development.

## Features

- ✅ User Authentication (Login/Register)
- ✅ Create, Read, Update Blog Posts
- ✅ Categories and Tags
- ✅ Comment System
- ✅ AJAX Search
- ✅ Responsive Design
- ✅ Admin Panel
- ✅ Dark/Light Theme

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, JavaScript (ES6+)
- **Database**: SQLite (development), PostgreSQL (production)
- **Forms**: WTForms with validation

## Quick Start

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\\Scripts\\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the app: `python run.py`
6. Visit: http://localhost:5000

## Default Login
- Email: admin@example.com
- Password: admin123

## License
MIT License
