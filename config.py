import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Clé secrète
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-scms-2024-change-in-production'
    
    # Base de données - PostgreSQL pour Render
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Si DATABASE_URL commence par postgres://, remplacer par postgresql://
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads - Utiliser un service externe ou stocker en base64
    UPLOAD_FOLDER = '/tmp/uploads'  # Dossier temporaire sur Render
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB
    
    # Extensions autorisées
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'txt',
        'jpg', 'jpeg', 'png', 'gif'
    }
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # Admin credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Application settings
    APPLICATION_NAME = "SCMS SARL - Candidatures"
    DATE_LIMITE = datetime(2026, 2, 24).date()
    
    # Emails de contact
    EMAIL_CONTACT = os.environ.get('EMAIL_CONTACT', 'scsmaubma@gmail.com')
    EMAIL_SUPPORT = os.environ.get('EMAIL_SUPPORT', 'support@scsmaubmar.org')
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = 3600  # 1 heure
    
    @staticmethod
    def init_app(app):
        # Créer le dossier temporaire pour uploads
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)