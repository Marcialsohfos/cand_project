import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Clé secrète
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-scms-2024-change-in-production'
    
    # Base de données
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'scms_candidatures.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
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
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # Admin credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')  # Mot de passe en clair pour dev
    ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')  # Hash généré avec werkzeug.security
    
    # Application settings
    APPLICATION_NAME = "SCMS SARL - Candidatures"
    DATE_LIMITE = datetime(2026, 01, 31).date()
    
    # Emails de contact
    EMAIL_CONTACT = os.environ.get('EMAIL_CONTACT', 'scsmaubma@gmail.com')
    EMAIL_SUPPORT = os.environ.get('EMAIL_SUPPORT', 'support@scsmaubmar.org')
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = 3600  # 1 heure
    
    @staticmethod
    def init_app(app):
        # Créer les dossiers nécessaires
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        # Pour SQLite, créer le dossier instance
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # En production, utiliser PostgreSQL ou MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # En production, SECRET_KEY doit être définie dans les variables d'environnement
    SECRET_KEY = os.environ.get('SECRET_KEY')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig

}
