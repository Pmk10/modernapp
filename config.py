# config.py - Application Configuration

"""
Flask Application Configuration

This module contains configuration classes for different environments:
- DevelopmentConfig: For local development
- ProductionConfig: For production deployment
- TestingConfig: For running tests

Environment variables can override default settings.
"""

import os
from datetime import timedelta

# Base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration class.
    
    Contains common configuration settings that apply to all environments.
    Other configuration classes inherit from this base class.
    """
    
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    
    # Pagination
    POSTS_PER_PAGE = 6
    COMMENTS_PER_PAGE = 10
    
    # Email Configuration (Optional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Admin Configuration
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
    }
    
    @staticmethod
    def init_app(app):
        """
        Initialize application with configuration-specific settings.
        
        This method can be overridden in subclasses to perform
        environment-specific initialization.
        """
        pass

class DevelopmentConfig(Config):
    """
    Development environment configuration.
    
    Used during local development. Includes debug mode,
    detailed error pages, and a local SQLite database.
    """
    
    # Enable debug mode
    DEBUG = True
    
    # Database - SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'blog_dev.db')
    
    # Detailed SQL query logging
    SQLALCHEMY_ECHO = False  # Set to True to see SQL queries
    
    # Development-specific settings
    WTF_CSRF_TIME_LIMIT = None  # Disable CSRF timeout in dev
    TEMPLATES_AUTO_RELOAD = True
    
    @staticmethod
    def init_app(app):
        """Initialize development-specific settings."""
        Config.init_app(app)
        
        # Create upload directory if it doesn't exist
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
        
        print("🔧 Development mode initialized")

class ProductionConfig(Config):
    """
    Production environment configuration.
    
    Used for deployed applications. Includes security settings,
    production database, and optimized configurations.
    """
    
    # Disable debug mode
    DEBUG = False
    
    # Database - Use environment variable for production DB
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'blog.db')
    
    # Handle Heroku's postgres:// URL format
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Production security settings
    SSL_REDIRECT = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour CSRF timeout
    
    # Performance settings
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = -1
    
    @staticmethod
    def init_app(app):
        """Initialize production-specific settings."""
        Config.init_app(app)
        
        # Add security headers
        @app.after_request
        def add_security_headers(response):
            for header, value in Config.SECURITY_HEADERS.items():
                response.headers[header] = value
            return response
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        
        print("🚀 Production mode initialized")

class TestingConfig(Config):
    """
    Testing environment configuration.
    
    Used when running tests. Includes in-memory database,
    disabled CSRF protection, and testing-specific settings.
    """
    
    # Enable testing mode
    TESTING = True
    
    # In-memory SQLite database for fast tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for easier testing
    WTF_CSRF_ENABLED = False
    
    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 1
    
    # Disable login rate limiting in tests
    LOGIN_DISABLED = True
    
    @staticmethod
    def init_app(app):
        """Initialize testing-specific settings."""
        Config.init_app(app)
        print("🧪 Testing mode initialized")

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """
    Get the appropriate configuration class based on environment.
    
    Returns:
        Config class: The configuration class for the current environment
    """
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])