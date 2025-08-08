# app.py - Main Flask Application

"""
Flask Blog Application

This module contains the main Flask application factory and all route handlers.
It demonstrates the concepts from your curriculum including:
- Flask basics (routes, templates, Jinja2)
- Database integration (SQLAlchemy)
- Form handling (WTForms)
- Authentication (Flask-Login)
- REST APIs and AJAX
- Error handling
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os


# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    """
    Application Factory Pattern
    
    Creates and configures the Flask application instance.
    This pattern allows for easy testing and multiple configurations.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    from config import get_config
    config_class = get_config()
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import models after db initialization
    from models import User, BlogPost, Category, Tag, Comment
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Create all database tables
    with app.app_context():
        db.create_all()
        create_sample_data_if_needed()
    
    return app

def create_sample_data_if_needed():
    """Create sample data if database is empty."""
    from models import Category, Tag, User, BlogPost
    
    if not Category.query.first():
        # Create default categories
        categories = [
            Category(name='Tutorial', description='Step-by-step guides and tutorials'),
            Category(name='Framework', description='Web frameworks and libraries'),
            Category(name='JavaScript', description='JavaScript programming and ES6+'),
            Category(name='CSS', description='Styling, layouts, and design systems'),
            Category(name='Accessibility', description='Web accessibility and inclusive design')
        ]
        for category in categories:
            db.session.add(category)
        
        # Create default tags
        tags = [
            Tag(name='HTML'), Tag(name='CSS'), Tag(name='JavaScript'),
            Tag(name='Bootstrap'), Tag(name='ES6'), Tag(name='Responsive'),
            Tag(name='Features'), Tag(name='Grid'), Tag(name='Flexbox'),
            Tag(name='A11y'), Tag(name='ARIA')
        ]
        for tag in tags:
            db.session.add(tag)
        
        # Create default admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        
        db.session.commit()
        print("✓ Sample data created!")

# Create Flask app instance
app = create_app()

# =============================================================================
# MAIN ROUTES
# =============================================================================

@app.route('/')
def index():
    """
    Homepage route - demonstrates Jinja2 templating
    
    WHY JINJA2: Server-side templating allows us to inject Python data
    directly into HTML templates, providing dynamic content generation.
    """
    from models import BlogPost, Category, Tag
    
    # Get featured post and recent posts
    featured_post = BlogPost.query.filter_by(featured=True).first()
    recent_posts = BlogPost.query.order_by(BlogPost.date_created.desc()).limit(6).all()
    
    # Get categories and tags for filtering
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # Pass data to template using Jinja2
    return render_template('index.html',
                         featured_post=featured_post,
                         recent_posts=recent_posts,
                         categories=categories,
                         tags=tags,
                         title='Home')

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    """
    Individual post view - demonstrates database queries and relationships
    
    WHY SQLALCHEMY: ORM provides an object-oriented way to interact with
    databases, making complex queries and relationships easy to manage.
    """
    from models import BlogPost
    
    # Get post or return 404
    post = BlogPost.query.get_or_404(post_id)
    
    # Get related posts from same category
    related_posts = BlogPost.query.filter(
        BlogPost.category_id == post.category_id,
        BlogPost.id != post_id
    ).limit(3).all()
    
    # Get comments for this post
    comments = post.comments.filter_by(approved=True).order_by('date_created').all()
    
    return render_template('blog/post_detail.html',
                         post=post,
                         related_posts=related_posts,
                         comments=comments,
                         title=post.title)

@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    """
    Create new blog post - demonstrates form handling with WTForms
    
    WHY WTFORMS: Provides server-side form validation, CSRF protection,
    and easy form rendering in templates.
    """
    from forms import BlogPostForm
    from models import BlogPost, Tag
    
    form = BlogPostForm()
    
    if form.validate_on_submit():
        # Create new post from form data
        post = BlogPost(
            title=form.title.data,
            content=form.content.data,
            excerpt=form.excerpt.data,
            author_id=current_user.id,
            category_id=form.category.data,
            featured=form.featured.data
        )
        
        # Handle tags - demonstrate many-to-many relationships
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',')]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('post_detail', post_id=post.id))
    
    return render_template('blog/create_post.html', 
                         form=form, 
                         title='Create Post')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login - demonstrates authentication with Flask-Login
    
    WHY FLASK-LOGIN: Provides session management, user authentication,
    and login protection for routes.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    from forms import LoginForm
    form = LoginForm()
    
    if form.validate_on_submit():
        from models import User
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', 
                         form=form, 
                         title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration - demonstrates form validation and database operations
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    from forms import RegisterForm
    from models import User
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', 
                         form=form, 
                         title='Register')

@app.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# =============================================================================
# REST API ENDPOINTS - Demonstrating AJAX Integration
# =============================================================================

@app.route('/api/posts', methods=['GET'])
def api_get_posts():
    """
    REST API endpoint for AJAX requests
    
    WHY AJAX: Allows asynchronous data loading without page reloads,
    enabling dynamic content updates and improved user experience.
    """
    from models import BlogPost, Tag
    
    # Get query parameters for filtering
    category_id = request.args.get('category_id', type=int)
    tag_name = request.args.get('tag')
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)
    
    # Build query with filters
    query = BlogPost.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if tag_name:
        query = query.join(BlogPost.tags).filter(Tag.name == tag_name)
    
    if search_query:
        query = query.filter(
            BlogPost.title.contains(search_query) |
            BlogPost.content.contains(search_query) |
            BlogPost.excerpt.contains(search_query)
        )
    
    # Paginate results
    posts = query.order_by(BlogPost.date_created.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Convert to JSON format
    posts_data = []
    for post in posts.items:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'excerpt': post.excerpt,
            'author': post.author.username,
            'date': post.date_created.strftime('%Y-%m-%d'),
            'category': post.category.name,
            'tags': [tag.name for tag in post.tags],
            'read_time': post.read_time,
            'featured': post.featured,
            'url': url_for('post_detail', post_id=post.id)
        })
    
    return jsonify({
        'posts': posts_data,
        'total': posts.total,
        'pages': posts.pages,
        'current_page': posts.page,
        'has_next': posts.has_next,
        'has_prev': posts.has_prev
    })

@app.route('/api/search', methods=['POST'])
def api_search():
    """
    AJAX search endpoint for live search functionality
    
    WHY AJAX: Enables real-time search without page reloads,
    providing instant feedback to users as they type.
    """
    from models import BlogPost
    
    data = request.get_json()
    search_term = data.get('search', '').strip()
    
    if not search_term or len(search_term) < 3:
        return jsonify({'results': []})
    
    # Search in posts
    posts = BlogPost.query.filter(
        BlogPost.title.contains(search_term) |
        BlogPost.content.contains(search_term) |
        BlogPost.excerpt.contains(search_term)
    ).limit(10).all()
    
    results = []
    for post in posts:
        results.append({
            'id': post.id,
            'title': post.title,
            'excerpt': post.excerpt[:100] + '...' if len(post.excerpt) > 100 else post.excerpt,
            'url': url_for('post_detail', post_id=post.id),
            'category': post.category.name,
            'author': post.author.username,
            'date': post.date_created.strftime('%B %d, %Y')
        })
    
    return jsonify({'results': results})

@app.route('/api/comment', methods=['POST'])
@login_required
def api_add_comment():
    """
    AJAX endpoint for adding comments
    
    WHY AJAX: Allows users to add comments without page refresh,
    providing seamless interaction experience.
    """
    from models import Comment, BlogPost
    
    data = request.get_json()
    post_id = data.get('post_id')
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Comment content is required'}), 400
    
    post = BlogPost.query.get_or_404(post_id)
    
    comment = Comment(
        content=content,
        author_id=current_user.id,
        post_id=post_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.username,
            'date': comment.date_created.strftime('%Y-%m-%d %H:%M')
        }
    })

@app.route('/api/categories')
def api_get_categories():
    """API endpoint to get all categories."""
    from models import Category
    categories = Category.query.all()
    return jsonify({
        'categories': [{'id': cat.id, 'name': cat.name, 'post_count': len(cat.posts)} 
                      for cat in categories]
    })

@app.route('/api/tags')
def api_get_tags():
    """API endpoint to get all tags."""
    from models import Tag
    tags = Tag.query.all()
    return jsonify({
        'tags': [{'name': tag.name, 'post_count': len(tag.posts)} for tag in tags]
    })

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors with custom template."""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with custom template."""
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    """
    Direct run (not recommended for production)
    Use run.py instead for proper application startup.
    """
    app.run(debug=True)