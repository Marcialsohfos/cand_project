from datetime import datetime
from app import db

class Candidature(db.Model):
    __tablename__ = 'candidatures'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informations personnelles
    nom_complet = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    telephone = db.Column(db.String(20))
    ville = db.Column(db.String(100), nullable=False)
    
    # Documents
    cv_path = db.Column(db.String(500))
    lettre_motivation_path = db.Column(db.String(500))
    portfolio_fichier_path = db.Column(db.String(500))
    portfolio_lien = db.Column(db.String(500))
    
    # Contenu textuel
    lettre_motivation_text = db.Column(db.Text)
    competences_marketing = db.Column(db.Text)
    
    # Métadonnées
    date_soumission = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(20), default='nouvelle')  # nouvelle, en_revue, rejetee, acceptee
    notes = db.Column(db.Text)
    
    # Adresse IP (pour sécurité)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom_complet': self.nom_complet,
            'email': self.email,
            'telephone': self.telephone,
            'ville': self.ville,
            'date_soumission': self.date_soumission.isoformat() if self.date_soumission else None,
            'statut': self.statut,
            'has_cv': bool(self.cv_path),
            'has_lettre': bool(self.lettre_motivation_path),
            'has_portfolio_file': bool(self.portfolio_fichier_path),
            'portfolio_lien': self.portfolio_lien
        }
    
    def __repr__(self):
        return f'<Candidature {self.nom_complet} - {self.email}>'


class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'
