# forms.py - WTForms Form Classes

"""
Flask-WTF Forms for the Blog Application

This module defines all form classes using WTForms for:
- User authentication (login, registration)
- Blog post creation and editing
- Comment submission
- Search functionality

WHY WTFORMS: Provides server-side form validation, CSRF protection,
automatic form rendering, and secure form handling.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, Regexp
from wtforms.widgets import TextArea

# =============================================================================
# CUSTOM VALIDATORS
# =============================================================================

def unique_username(form, field):
    """Custom validator to check if username is unique."""
    # We'll import here to avoid circular imports
    from models import User
    user = User.query.filter_by(username=field.data).first()
    if user:
        raise ValidationError('Username already exists. Please choose a different one.')

def unique_email(form, field):
    """Custom validator to check if email is unique."""
    from models import User
    user = User.query.filter_by(email=field.data).first()
    if user:
        raise ValidationError('Email already registered. Please use a different email.')

# =============================================================================
# AUTHENTICATION FORMS
# =============================================================================

class LoginForm(FlaskForm):
    """
    User login form with validation.
    
    WHY WTFORMS: Provides automatic CSRF protection, validation,
    and easy form rendering in Jinja2 templates.
    
    Fields:
    - email: User's email address
    - password: User's password
    - remember_me: Keep user logged in
    """
    
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.'),
        Length(max=120, message='Email must be less than 120 characters.')
    ], render_kw={
        'placeholder': 'Enter your email address',
        'class': 'form-control',
        'autocomplete': 'email'
    })
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=6, message='Password must be at least 6 characters long.')
    ], render_kw={
        'placeholder': 'Enter your password',
        'class': 'form-control',
        'autocomplete': 'current-password'
    })
    
    remember_me = BooleanField('Remember Me', render_kw={
        'class': 'form-check-input'
    })

class RegisterForm(FlaskForm):
    """
    User registration form with comprehensive validation.
    
    WHY WTFORMS: Handles complex validation rules, password confirmation,
    and provides detailed error messages for better UX.
    
    Fields:
    - username: Unique username (4-20 characters)
    - email: Unique email address
    - first_name: User's first name (optional)
    - last_name: User's last name (optional)
    - password: Secure password (min 8 characters)
    - password2: Password confirmation
    """
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required.'),
        Length(min=4, max=20, message='Username must be between 4 and 20 characters.'),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 
               'Username must start with a letter and contain only letters, numbers, dots, or underscores.'),
        unique_username
    ], render_kw={
        'placeholder': 'Choose a unique username',
        'class': 'form-control',
        'autocomplete': 'username'
    })
    
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.'),
        Length(max=120, message='Email must be less than 120 characters.'),
        unique_email
    ], render_kw={
        'placeholder': 'Enter your email address',
        'class': 'form-control',
        'autocomplete': 'email'
    })
    
    first_name = StringField('First Name', validators=[
        Optional(),
        Length(max=50, message='First name must be less than 50 characters.')
    ], render_kw={
        'placeholder': 'Enter your first name (optional)',
        'class': 'form-control',
        'autocomplete': 'given-name'
    })
    
    last_name = StringField('Last Name', validators=[
        Optional(),
        Length(max=50, message='Last name must be less than 50 characters.')
    ], render_kw={
        'placeholder': 'Enter your last name (optional)',
        'class': 'form-control',
        'autocomplete': 'family-name'
    })
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=8, message='Password must be at least 8 characters long.'),
    ], render_kw={
        'placeholder': 'Create a strong password',
        'class': 'form-control',
        'autocomplete': 'new-password'
    })
    
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ], render_kw={
        'placeholder': 'Confirm your password',
        'class': 'form-control',
        'autocomplete': 'new-password'
    })

# =============================================================================
# BLOG CONTENT FORMS
# =============================================================================

class CKTextAreaWidget(TextArea):
    """Custom widget for rich text editor integration."""
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'form-control ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class BlogPostForm(FlaskForm):
    """
    Blog post creation and editing form.
    
    WHY WTFORMS: Handles complex form data including relationships
    (categories, tags), file uploads, and content validation.
    
    Fields:
    - title: Post title (5-200 characters)
    - excerpt: Short description (optional)
    - content: Main post content (rich text)
    - category: Post category (dropdown)
    - tags: Comma-separated tags
    - featured_image: Image upload (optional)
    - featured: Mark as featured post
    - published: Publish status
    """
    
    title = StringField('Post Title', validators=[
        DataRequired(message='Title is required.'),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters.')
    ], render_kw={
        'placeholder': 'Enter an engaging post title',
        'class': 'form-control',
        'maxlength': '200'
    })
    
    excerpt = TextAreaField('Excerpt', validators=[
        Optional(),
        Length(max=500, message='Excerpt cannot exceed 500 characters.')
    ], render_kw={
        'placeholder': 'Write a brief excerpt (optional - will be auto-generated if left empty)',
        'class': 'form-control',
        'rows': '3',
        'maxlength': '500'
    })
    
    content = TextAreaField('Content', validators=[
        DataRequired(message='Content is required.'),
        Length(min=50, message='Content must be at least 50 characters long.')
    ], render_kw={
        'placeholder': 'Write your blog post content here...',
        'class': 'form-control',
        'rows': '15'
    })
    
    category = SelectField('Category', coerce=int, validators=[
        DataRequired(message='Please select a category.')
    ], render_kw={
        'class': 'form-select'
    })
    
    tags = StringField('Tags', validators=[
        Optional(),
        Length(max=200, message='Tags cannot exceed 200 characters.')
    ], render_kw={
        'placeholder': 'Enter tags separated by commas (e.g., python, flask, web-development)',
        'class': 'form-control',
        'data-toggle': 'tooltip',
        'data-placement': 'top',
        'title': 'Separate multiple tags with commas'
    })
    
    featured_image = FileField('Featured Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                   message='Only image files are allowed (JPG, JPEG, PNG, GIF, WebP).')
    ], render_kw={
        'class': 'form-control',
        'accept': 'image/*'
    })
    
    featured = BooleanField('Featured Post', render_kw={
        'class': 'form-check-input'
    })
    
    published = BooleanField('Publish Now', default=True, render_kw={
        'class': 'form-check-input'
    })
    
    def __init__(self, *args, **kwargs):
        """Initialize form with dynamic category choices."""
        super(BlogPostForm, self).__init__(*args, **kwargs)
        # Import here to avoid circular imports
        from models import Category
        # Populate category choices from database
        self.category.choices = [(0, 'Select a category...')] + \
                               [(cat.id, cat.name) for cat in Category.query.order_by(Category.name).all()]

class EditPostForm(BlogPostForm):
    """
    Post editing form (inherits from BlogPostForm).
    
    Removes unique validation constraints that might conflict
    with editing existing posts.
    """
    pass

# =============================================================================
# COMMENT FORMS
# =============================================================================

class CommentForm(FlaskForm):
    """
    Comment submission form.
    
    WHY WTFORMS: Provides validation for user-generated content,
    CSRF protection against spam, and automatic form rendering.
    
    Fields:
    - content: Comment text (10-1000 characters)
    """
    
    content = TextAreaField('Your Comment', validators=[
        DataRequired(message='Comment content is required.'),
        Length(min=10, max=1000, message='Comment must be between 10 and 1000 characters.')
    ], render_kw={
        'placeholder': 'Share your thoughts about this post...',
        'class': 'form-control',
        'rows': '4',
        'maxlength': '1000'
    })

class ReplyForm(FlaskForm):
    """Reply to comment form (simplified comment form)."""
    
    content = TextAreaField('Your Reply', validators=[
        DataRequired(message='Reply content is required.'),
        Length(min=5, max=500, message='Reply must be between 5 and 500 characters.')
    ], render_kw={
        'placeholder': 'Write your reply...',
        'class': 'form-control',
        'rows': '3',
        'maxlength': '500'
    })

# =============================================================================
# SEARCH AND FILTER FORMS
# =============================================================================

class SearchForm(FlaskForm):
    """
    Search form for blog posts.
    
    WHY WTFORMS: Handles search input validation and provides
    CSRF protection for search requests.
    
    Fields:
    - query: Search term (3-100 characters)
    """
    
    query = StringField('Search', validators=[
        DataRequired(message='Please enter a search term.'),
        Length(min=3, max=100, message='Search term must be between 3 and 100 characters.')
    ], render_kw={
        'placeholder': 'Search posts, categories, tags...',
        'class': 'form-control',
        'autocomplete': 'off'
    })

class FilterForm(FlaskForm):
    """
    Advanced filtering form for blog posts.
    
    Fields:
    - category: Filter by category
    - tag: Filter by tag
    - author: Filter by author
    - date_range: Filter by date range
    """
    
    category = SelectField('Category', coerce=int, validators=[Optional()], 
                          render_kw={'class': 'form-select'})
    
    tag = StringField('Tag', validators=[Optional()], 
                     render_kw={'class': 'form-control', 'placeholder': 'Filter by tag'})
    
    author = StringField('Author', validators=[Optional()], 
                        render_kw={'class': 'form-control', 'placeholder': 'Filter by author'})
    
    def __init__(self, *args, **kwargs):
        """Initialize form with dynamic choices."""
        super(FilterForm, self).__init__(*args, **kwargs)
        from models import Category
        self.category.choices = [(0, 'All Categories')] + \
                               [(cat.id, cat.name) for cat in Category.query.order_by(Category.name).all()]

# =============================================================================
# FORM HELPER FUNCTIONS
# =============================================================================

def flash_form_errors(form):
    """
    Flash all form validation errors.
    
    This helper function extracts validation errors from a form
    and displays them as flash messages to the user.
    
    Args:
        form: The form instance with validation errors
    """
    from flask import flash
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{getattr(form, field).label.text}: {error}', 'error')