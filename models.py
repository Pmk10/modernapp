# models.py - Database Models

"""
Database Models using SQLAlchemy ORM

This module defines all database models for the blog application:
- User: User authentication and profile
- Category: Blog post categories
- Tag: Blog post tags
- BlogPost: Main blog content
- Comment: User comments on posts

WHY SQLALCHEMY: Object-Relational Mapping (ORM) provides a Python interface
to interact with databases using classes and objects instead of SQL queries.
"""
# Import db from app module - we'll fix this circular import
from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# =============================================================================
# ASSOCIATION TABLES for Many-to-Many Relationships
# =============================================================================

# Association table for BlogPost ↔ Tag many-to-many relationship
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('blog_post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# =============================================================================
# USER MODEL - Authentication and User Management
# =============================================================================

class User(UserMixin, db.Model):
    """
    User model for authentication and user profiles.
    
    Inherits from UserMixin for Flask-Login integration, providing
    methods like is_authenticated, is_active, etc.
    
    Relationships:
    - One-to-many with BlogPost (user can write many posts)
    - One-to-many with Comment (user can write many comments)
    """
    
    __tablename__ = 'user'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # User credentials
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(200))
    
    # User status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('BlogPost', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """Initialize user with default values."""
        super(User, self).__init__(**kwargs)
    
    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def post_count(self):
        """Get number of posts by this user."""
        return self.posts.count()
    
    def to_dict(self):
        """Convert user to dictionary for JSON responses."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'bio': self.bio,
            'is_admin': self.is_admin,
            'post_count': self.post_count,
            'date_created': self.date_created.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

# =============================================================================
# CATEGORY MODEL - Blog Post Organization
# =============================================================================

class Category(db.Model):
    """
    Category model for organizing blog posts.
    
    Categories provide a way to group related blog posts together.
    Each post belongs to exactly one category (one-to-many relationship).
    """
    
    __tablename__ = 'category'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Category information
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#007bff')  # Hex color code
    icon = db.Column(db.String(50), default='bi-folder')  # Bootstrap icon class
    
    # SEO fields
    slug = db.Column(db.String(60), unique=True, index=True)
    
    # Timestamps
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    posts = db.relationship('BlogPost', backref='category', lazy='dynamic')
    
    def __init__(self, **kwargs):
        """Initialize category with auto-generated slug."""
        super(Category, self).__init__(**kwargs)
        if self.name and not self.slug:
            self.slug = self.generate_slug()
    
    def generate_slug(self):
        """Generate URL-friendly slug from name."""
        import re
        slug = re.sub(r'[^\w\s-]', '', self.name.lower())
        slug = re.sub(r'[\s_-]+', '-', slug)
        return slug.strip('-')
    
    @property
    def post_count(self):
        """Get number of posts in this category."""
        return self.posts.count()
    
    def to_dict(self):
        """Convert category to dictionary for JSON responses."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'slug': self.slug,
            'post_count': self.post_count
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'

# =============================================================================
# TAG MODEL - Blog Post Tagging
# =============================================================================

class Tag(db.Model):
    """
    Tag model for blog post tagging system.
    
    Tags provide a flexible way to categorize and filter blog posts.
    Posts can have multiple tags, and tags can be associated with multiple posts
    (many-to-many relationship via post_tags association table).
    """
    
    __tablename__ = 'tag'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Tag information
    name = db.Column(db.String(30), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200))
    color = db.Column(db.String(7), default='#6c757d')  # Hex color code
    
    # Timestamps
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Many-to-many relationship with BlogPost (defined in BlogPost model)
    
    @property
    def post_count(self):
        """Get number of posts with this tag."""
        return len(self.posts)
    
    def to_dict(self):
        """Convert tag to dictionary for JSON responses."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'post_count': self.post_count
        }
    
    def __repr__(self):
        return f'<Tag {self.name}>'

# =============================================================================
# BLOG POST MODEL - Main Content
# =============================================================================

class BlogPost(db.Model):
    """
    Blog post model - the main content entity.
    
    Relationships:
    - Many-to-one with User (author)
    - Many-to-one with Category
    - Many-to-many with Tag
    - One-to-many with Comment
    
    WHY RELATIONSHIPS: SQLAlchemy relationships allow us to easily access
    related data without complex SQL joins, making code more readable and maintainable.
    """
    
    __tablename__ = 'blog_post'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Content fields
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500))
    
    # SEO and display fields
    slug = db.Column(db.String(250), unique=True, index=True)
    meta_description = db.Column(db.String(160))
    featured_image = db.Column(db.String(200))
    
    # Post status
    published = db.Column(db.Boolean, default=True, nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    allow_comments = db.Column(db.Boolean, default=True, nullable=False)
    
    # Reading metrics
    read_time = db.Column(db.String(20), default='5 min read')
    view_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Timestamps
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    date_published = db.Column(db.DateTime)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Relationships
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery',
                          backref=db.backref('posts', lazy=True))
    comments = db.relationship('Comment', backref='post', lazy='dynamic', 
                              cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """Initialize blog post with auto-generated fields."""
        super(BlogPost, self).__init__(**kwargs)
        if self.title and not self.slug:
            self.slug = self.generate_slug()
        if not self.excerpt and self.content:
            self.excerpt = self.generate_excerpt()
        if not self.read_time and self.content:
            self.read_time = self.calculate_read_time()
        if self.published and not self.date_published:
            self.date_published = datetime.utcnow()
    
    def generate_slug(self):
        """Generate URL-friendly slug from title."""
        import re
        slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        slug = re.sub(r'[\s_-]+', '-', slug)
        base_slug = slug.strip('-')
        
        # Ensure uniqueness
        counter = 1
        unique_slug = base_slug
        while BlogPost.query.filter_by(slug=unique_slug).first():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        
        return unique_slug
    
    def generate_excerpt(self, length=150):
        """Generate excerpt from content."""
        if len(self.content) <= length:
            return self.content
        return self.content[:length].rsplit(' ', 1)[0] + '...'
    
    def calculate_read_time(self):
        """Calculate estimated reading time."""
        word_count = len(self.content.split())
        minutes = max(1, word_count // 200)  # Average 200 words per minute
        return f"{minutes} min read"
    
    @property
    def tag_list(self):
        """Get comma-separated list of tag names."""
        return ', '.join([tag.name for tag in self.tags])
    
    @property
    def comment_count(self):
        """Get number of approved comments."""
        return self.comments.filter_by(approved=True).count()
    
    def to_dict(self):
        """Convert blog post to dictionary for JSON responses."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'slug': self.slug,
            'published': self.published,
            'featured': self.featured,
            'read_time': self.read_time,
            'view_count': self.view_count,
            'author': self.author.username,
            'category': self.category.name,
            'tags': [tag.name for tag in self.tags],
            'comment_count': self.comment_count,
            'date_created': self.date_created.isoformat(),
            'date_published': self.date_published.isoformat() if self.date_published else None
        }
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'

# =============================================================================
# COMMENT MODEL - User Comments
# =============================================================================

class Comment(db.Model):
    """
    Comment model for user comments on blog posts.
    
    Relationships:
    - Many-to-one with User (commenter)
    - Many-to-one with BlogPost (commented post)
    
    WHY COMMENTS: Demonstrates one-to-many relationships and content moderation.
    """
    
    __tablename__ = 'comment'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Comment content
    content = db.Column(db.Text, nullable=False)
    
    # Moderation
    approved = db.Column(db.Boolean, default=True, nullable=False)
    flagged = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    
    # Optional: Reply threading (self-referential relationship)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self):
        """Convert comment to dictionary for JSON responses."""
        return {
            'id': self.id,
            'content': self.content,
            'approved': self.approved,
            'author': self.author.username,
            'post_id': self.post_id,
            'date_created': self.date_created.isoformat()
        }
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.author.username}>'