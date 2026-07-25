import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-secret-key')
DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///tasks.db')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER', 'dev@example.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'dev-only-password')
