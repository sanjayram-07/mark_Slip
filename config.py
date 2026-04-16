# Application Configuration Management

import os
from datetime import timedelta

class BaseConfig:
    """Base configuration - common to all environments"""
    
    # Flask
    JSONIFY_PRETTYPRINT_REGULAR = False
    JSON_SORT_KEYS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp')
    
    # Defaults
    COLLEGE_NAME = os.getenv('COLLEGE_NAME', 'Madras Institute of Technology')
    DEPARTMENT_NAME = os.getenv('DEPARTMENT_NAME', 'Department of Computer Technology')


class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Allow all CORS origins in development
    CORS_ORIGINS = ['*']


class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Production requires SECRET_KEY to be set
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    # Strict CORS in production
    CORS_ORIGINS = [
        os.getenv('ALLOWED_DOMAIN', 'localhost'),
        os.getenv('ALLOWED_DOMAIN_2', '')
    ]
    
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PREFERRED_URL_SCHEME = 'https'


class TestingConfig(BaseConfig):
    """Testing environment configuration"""
    
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'testing-secret-key'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Use in-memory storage for tests
    UPLOAD_FOLDER = '/tmp/test_uploads'


# Configuration factory
def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    config_class = configs.get(env, DevelopmentConfig)
    return config_class


if __name__ == '__main__':
    # Display current configuration
    env = os.getenv('FLASK_ENV', 'development')
    config = get_config(env)
    
    print(f"Environment: {env}")
    print(f"Debug: {config.DEBUG}")
    print(f"Testing: {config.TESTING}")
    print(f"Max File Size: {config.MAX_FILE_SIZE / (1024*1024):.1f}MB")
    print(f"Upload Folder: {config.UPLOAD_FOLDER}")
