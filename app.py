import os
import json
import zipfile
import base64
from datetime import datetime
from io import BytesIO
from functools import wraps
import threading
from flask import Flask, render_template, request, jsonify, send_file, url_for, flash, redirect, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation des extensions
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()

# Modèle Candidature avec stockage optimisé
class Candidature(db.Model):
    __tablename__ = 'candidatures'
    
    id = db.Column(db.Integer, primary_key=True)
    # Informations personnelles
    nom_complet = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telephone = db.Column(db.String(20))
    ville = db.Column(db.String(100))
    portfolio_lien = db.Column(db.String(500))
    
    # Stockage optimisé : seuls les petits fichiers en base64
    cv_data = db.Column(db.Text)  # Pour les petits CV
    cv_filename = db.Column(db.String(500))
    cv_size = db.Column(db.Integer)  # Taille en bytes
    
    lettre_motivation_data = db.Column(db.Text)
    lettre_motivation_filename = db.Column(db.String(500))
    lettre_motivation_size = db.Column(db.Integer)
    
    portfolio_fichier_data = db.Column(db.Text)
    portfolio_fichier_filename = db.Column(db.String(500))
    portfolio_fichier_size = db.Column(db.Integer)
    
    lettre_motivation_text = db.Column(db.Text)
    competences_marketing = db.Column(db.Text)
    
    # Métadonnées
    date_soumission = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(50), default='Nouvelle')
    notes_admin = db.Column(db.Text)
    
    # Pour suivi des performances
    temps_traitement = db.Column(db.Float)  # Temps en secondes
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom_complet': self.nom_complet,
            'email': self.email,
            'telephone': self.telephone,
            'ville': self.ville,
            'date_soumission': self.date_soumission.isoformat() if self.date_soumission else None,
            'statut': self.statut,
            'has_cv': bool(self.cv_data),
            'has_lettre': bool(self.lettre_motivation_data),
            'has_portfolio': bool(self.portfolio_fichier_data)
        }


# Décorateur pour protéger les routes admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# Fonction pour envoyer les emails en arrière-plan
def send_emails_async(app, candidature_id):
    """Envoyer les emails en arrière-plan dans un thread séparé"""
    with app.app_context():
        try:
            candidature = Candidature.query.get(candidature_id)
            if not candidature:
                logger.error(f"Candidature {candidature_id} non trouvée pour l'envoi d'email")
                return
            
            # Email de confirmation au candidat
            try:
                msg = Message(
                    subject="Confirmation de réception de votre candidature - SCSM SARL",
                    recipients=[candidature.email],
                    sender=app.config['MAIL_DEFAULT_SENDER']
                )
                
                msg.body = f"""
                Bonjour {candidature.nom_complet},
                
                Nous accusons réception de votre candidature pour le poste chez SCSM SARL.
                
                Détails de votre soumission:
                - Date: {candidature.date_soumission.strftime('%d/%m/%Y %H:%M')}
                - Référence: CAND{candidature.id:06d}
                
                Nous examinerons votre dossier avec attention et vous contacterons si votre profil retient notre attention.
                
                Date limite de candidature: {app.config['DATE_LIMITE'].strftime('%d/%m/%Y')}
                
                Pour toute question, contactez-nous à:
                - Email: {app.config.get('EMAIL_CONTACT', 'contact@example.com')}
                - Support: {app.config.get('EMAIL_SUPPORT', 'support@example.com')}
                
                Cordialement,
                L'équipe de recrutement SCSM SARL
                """
                
                mail.send(msg)
                logger.info(f"Email de confirmation envoyé à {candidature.email}")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'email de confirmation: {str(e)}")
            
            # Notification admin
            try:
                admin_email = app.config.get('EMAIL_CONTACT')
                if admin_email:
                    msg = Message(
                        subject=f"[SCSM] Nouvelle candidature: {candidature.nom_complet}",
                        recipients=[admin_email],
                        sender=app.config['MAIL_DEFAULT_SENDER']
                    )
                    
                    msg.body = f"""
                    Nouvelle candidature reçue:
                    
                    Candidat: {candidature.nom_complet}
                    Email: {candidature.email}
                    Téléphone: {candidature.telephone}
                    Ville: {candidature.ville}
                    Date: {candidature.date_soumission.strftime('%d/%m/%Y %H:%M')}
                    ID: CAND{candidature.id:06d}
                    
                    Pour voir les détails, connectez-vous à l'interface admin.
                    """
                    
                    mail.send(msg)
                    logger.info(f"Notification admin envoyée pour candidature {candidature.id}")
                    
            except Exception as e:
                logger.error(f"Erreur notification admin: {str(e)}")
                
        except Exception as e:
            logger.error(f"Erreur dans send_emails_async: {str(e)}")


def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration pour Render
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-scms-2024-change-in-production')
    
    # Base de données PostgreSQL pour Render
    database_url = os.environ.get('DATABASE_URL')
    
    # Correction pour PostgreSQL sur Render
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///scms_candidatures.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Uploads - Limites de taille réduites pour optimisation
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max (optimisé)
    
    # Extensions autorisées
    app.config['ALLOWED_EXTENSIONS'] = {
        'pdf', 'doc', 'docx', 'txt',
        'jpg', 'jpeg', 'png', 'gif'
    }
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # Admin credentials
    app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
    app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Application settings
    app.config['APPLICATION_NAME'] = "SCMS SARL - Candidatures"
    app.config['DATE_LIMITE'] = datetime(2026, 2, 24).date()
    
    # Emails de contact
    app.config['EMAIL_CONTACT'] = os.environ.get('EMAIL_CONTACT', 'scsmaubma@gmail.com')
    app.config['EMAIL_SUPPORT'] = os.environ.get('EMAIL_SUPPORT', 'support@scsmaubmar.org')
    
    # Session settings
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 heure
    
    # Optimisation : compression des fichiers
    app.config['COMPRESS_FILES'] = True
    
    # Créer le dossier temporaire pour uploads
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialiser les extensions
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Créer les tables si elles n'existent pas
    with app.app_context():
        db.create_all()
    
    # Helper functions
    def allowed_file(filename):
        """Vérifier si l'extension du fichier est autorisée"""
        if not filename or '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in app.config['ALLOWED_EXTENSIONS']
    
    def process_file_upload(file, max_size=5*1024*1024):
        """Traiter un fichier uploadé de manière optimisée"""
        if not file or not file.filename:
            return None, None, None, 0
        
        try:
            # Lire le fichier en mémoire de manière optimisée
            file.seek(0, 2)  # Aller à la fin
            file_size = file.tell()  # Taille du fichier
            file.seek(0)  # Retour au début
            
            if file_size > max_size:
                logger.warning(f"Fichier trop volumineux: {file_size} > {max_size}")
                return None, None, None, file_size
            
            # Lire le contenu
            file_data = file.read()
            
            # Pour les petits fichiers, encoder en base64
            if file_size < 2*1024*1024:  # < 2MB
                encoded_data = base64.b64encode(file_data).decode('utf-8')
            else:
                # Pour les fichiers plus gros, stocker temporairement
                temp_filename = secure_filename(f"temp_{datetime.now().timestamp()}_{file.filename}")
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
                
                with open(temp_path, 'wb') as f:
                    f.write(file_data)
                encoded_data = temp_path  # Stocker le chemin
        
            # Informations sur le fichier
            original_name = secure_filename(file.filename)
            mimetype = file.mimetype or 'application/octet-stream'
            
            logger.info(f"Fichier traité: {original_name} ({file_size} bytes)")
            return encoded_data, original_name, mimetype, file_size
            
        except Exception as e:
            logger.error(f"Erreur traitement fichier {file.filename}: {str(e)}")
            return None, None, None, 0
    
    # Routes d'authentification admin
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        """Page de connexion admin"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Vérifier les identifiants
            if username == app.config['ADMIN_USERNAME']:
                if password == app.config.get('ADMIN_PASSWORD', ''):
                    session['admin_logged_in'] = True
                    session.permanent = True
                    flash('Connexion réussie!', 'success')
                    return redirect(url_for('admin_dashboard'))
            
            flash('Identifiants incorrects', 'error')
        
        return render_template('admin_login.html')
    
    @app.route('/admin/logout')
    def admin_logout():
        """Déconnexion admin"""
        session.pop('admin_logged_in', None)
        flash('Vous avez été déconnecté', 'info')
        return redirect(url_for('home'))
    
    # Routes admin protégées
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        """Tableau de bord admin"""
        stats = {
            'total': Candidature.query.count(),
            'nouvelles': Candidature.query.filter_by(statut='Nouvelle').count(),
            'en_revue': Candidature.query.filter_by(statut='En revue').count(),
            'contactees': Candidature.query.filter_by(statut='Contacté').count()
        }
        
        # Dernières candidatures
        recent_candidatures = Candidature.query.order_by(
            Candidature.date_soumission.desc()
        ).limit(10).all()
        
        return render_template('admin/dashboard.html', 
                             stats=stats, 
                             candidatures=recent_candidatures,
                             date_limite=app.config['DATE_LIMITE'])
    
    @app.route('/admin/candidatures')
    @admin_required
    def liste_candidatures():
        """Liste de toutes les candidatures"""
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Filtres
        statut = request.args.get('statut')
        search = request.args.get('search')
        
        query = Candidature.query
        
        if statut and statut != 'all':
            query = query.filter_by(statut=statut)
        
        if search:
            query = query.filter(
                db.or_(
                    Candidature.nom_complet.ilike(f'%{search}%'),
                    Candidature.email.ilike(f'%{search}%'),
                    Candidature.ville.ilike(f'%{search}%')
                )
            )
        
        candidatures = query.order_by(
            Candidature.date_soumission.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('admin/candidatures.html', 
                             candidatures=candidatures,
                             current_statut=statut,
                             search=search)
    
    @app.route('/admin/candidature/<int:id>', methods=['GET', 'POST'])
    @admin_required
    def voir_candidature(id):
        """Voir et modifier une candidature"""
        candidature = Candidature.query.get_or_404(id)
        
        if request.method == 'POST':
            # Mettre à jour le statut et les notes
            candidature.statut = request.form.get('statut', candidature.statut)
            candidature.notes_admin = request.form.get('notes_admin', candidature.notes_admin)
            
            db.session.commit()
            flash('Candidature mise à jour avec succès!', 'success')
            return redirect(url_for('voir_candidature', id=id))
        
        return render_template('admin/candidature_detail.html', 
                             candidature=candidature)
    
    @app.route('/admin/download/<int:id>/<string:document>')
    @admin_required
    def download_document(id, document):
        """Télécharger un document spécifique"""
        candidature = Candidature.query.get_or_404(id)
        
        file_info = {
            'cv': (candidature.cv_data, candidature.cv_filename),
            'lettre_motivation': (candidature.lettre_motivation_data, candidature.lettre_motivation_filename),
            'portfolio': (candidature.portfolio_fichier_data, candidature.portfolio_fichier_filename)
        }
        
        if document in file_info:
            file_data, filename = file_info[document]
            if file_data:
                try:
                    # Si c'est un chemin de fichier (fichiers volumineux)
                    if isinstance(file_data, str) and file_data.startswith('/tmp/'):
                        if os.path.exists(file_data):
                            return send_file(
                                file_data,
                                as_attachment=True,
                                download_name=filename or f"{document}_{candidature.id}"
                            )
                    
                    # Sinon, c'est du base64
                    file_bytes = base64.b64decode(file_data)
                    file_stream = BytesIO(file_bytes)
                    
                    return send_file(
                        file_stream,
                        as_attachment=True,
                        download_name=filename or f"{document}_{candidature.id}",
                        mimetype='application/octet-stream'
                    )
                except Exception as e:
                    logger.error(f"Erreur lors du téléchargement: {str(e)}")
        
        flash('Document non trouvé', 'error')
        return redirect(url_for('voir_candidature', id=id))
    
    # Route pour la page d'accueil
    @app.route('/home')
    @app.route('/')
    def home():
        """Page d'accueil avec navigation"""
        date_limite = app.config['DATE_LIMITE']
        aujourdhui = datetime.now().date()
        accepte_candidatures = aujourdhui <= date_limite
        
        return render_template('home.html', 
                             accepte_candidatures=accepte_candidatures,
                             date_limite=date_limite,
                             email_contact=app.config.get('EMAIL_CONTACT', 'contact@example.com'),
                             email_support=app.config.get('EMAIL_SUPPORT', 'support@example.com'))
    
    # Route pour le formulaire (séparée de l'accueil)
    @app.route('/formulaire')
    def formulaire():
        """Page du formulaire de candidature"""
        date_limite = app.config['DATE_LIMITE']
        aujourdhui = datetime.now().date()
        accepte_candidatures = aujourdhui <= date_limite
        
        if not accepte_candidatures:
            flash('La période de candidature est terminée.', 'warning')
            return redirect(url_for('home'))
        
        return render_template('index.html', 
                             accepte_candidatures=accepte_candidatures,
                             date_limite=date_limite)
    
    # Route de contact
    @app.route('/contact')
    def contact():
        """Page de contact"""
        return render_template('contact.html', 
                             email_contact=app.config.get('EMAIL_CONTACT', 'contact@example.com'),
                             email_support=app.config.get('EMAIL_SUPPORT', 'support@example.com'))
    
    # Routes publiques (candidats) - OPTIMISÉE
    @app.route('/postuler', methods=['POST'])
    def postuler():
        """Soumettre une candidature - Version optimisée"""
        import time
        start_time = time.time()
        
        # Vérifier la date limite
        aujourdhui = datetime.now().date()
        if aujourdhui > app.config['DATE_LIMITE']:
            return jsonify({
                'success': False, 
                'error': 'La période de candidature est terminée.'
            }), 400
        
        try:
            # Mesurer le temps
            processing_times = {}
            
            # Récupérer les données du formulaire
            candidature = Candidature()
            
            # Informations personnelles
            candidature.nom_complet = request.form.get('nom_complet', '').strip()
            candidature.email = request.form.get('email', '').strip()
            candidature.telephone = request.form.get('telephone', '').strip()
            candidature.ville = request.form.get('ville', '').strip()
            candidature.portfolio_lien = request.form.get('portfolio_lien', '').strip()
            candidature.lettre_motivation_text = request.form.get('motivation', '').strip()
            candidature.competences_marketing = request.form.get('competences', '').strip()
            
            # Validation rapide
            if not candidature.nom_complet or not candidature.email:
                return jsonify({'success': False, 'error': 'Nom complet et email sont obligatoires'}), 400
            
            file_status = {}
            
            # Traiter le CV (obligatoire)
            if 'cv' not in request.files:
                return jsonify({'success': False, 'error': 'Le CV est obligatoire'}), 400
            
            cv_file = request.files['cv']
            if cv_file and cv_file.filename:
                if allowed_file(cv_file.filename):
                    cv_data, cv_filename, cv_mimetype, cv_size = process_file_upload(cv_file)
                    if cv_data:
                        candidature.cv_data = cv_data
                        candidature.cv_filename = cv_filename
                        candidature.cv_size = cv_size
                        file_status['cv'] = f"CV uploadé ({cv_size//1024} KB)"
                    else:
                        return jsonify({'success': False, 'error': 'Erreur traitement CV'}), 400
                else:
                    return jsonify({'success': False, 'error': 'Extension CV non autorisée'}), 400
            
            # Traiter la lettre de motivation (obligatoire)
            if 'lettre_motivation' not in request.files:
                return jsonify({'success': False, 'error': 'La lettre de motivation est obligatoire'}), 400
            
            lettre_file = request.files['lettre_motivation']
            if lettre_file and lettre_file.filename:
                if allowed_file(lettre_file.filename):
                    lettre_data, lettre_filename, lettre_mimetype, lettre_size = process_file_upload(lettre_file)
                    if lettre_data:
                        candidature.lettre_motivation_data = lettre_data
                        candidature.lettre_motivation_filename = lettre_filename
                        candidature.lettre_motivation_size = lettre_size
                        file_status['lettre'] = f"Lettre uploadée ({lettre_size//1024} KB)"
                    else:
                        return jsonify({'success': False, 'error': 'Erreur traitement lettre'}), 400
            
            # Portfolio (optionnel)
            if 'portfolio_fichier' in request.files:
                portfolio_file = request.files['portfolio_fichier']
                if portfolio_file and portfolio_file.filename:
                    if allowed_file(portfolio_file.filename):
                        portfolio_data, portfolio_filename, portfolio_mimetype, portfolio_size = process_file_upload(portfolio_file)
                        if portfolio_data:
                            candidature.portfolio_fichier_data = portfolio_data
                            candidature.portfolio_fichier_filename = portfolio_filename
                            candidature.portfolio_fichier_size = portfolio_size
                            file_status['portfolio'] = f"Portfolio uploadé ({portfolio_size//1024} KB)"
            
            # Sauvegarder en base de données
            db.session.add(candidature)
            db.session.commit()
            
            processing_time = time.time() - start_time
            candidature.temps_traitement = processing_time
            db.session.commit()
            
            logger.info(f"Candidature {candidature.id} sauvegardée en {processing_time:.2f}s")
            
            # Lancer l'envoi des emails en arrière-plan (NE BLOQUE PAS LA RÉPONSE)
            try:
                email_thread = threading.Thread(
                    target=send_emails_async,
                    args=(app, candidature.id)
                )
                email_thread.daemon = True  # Thread démon (se termine avec l'app)
                email_thread.start()
                logger.info(f"Thread email lancé pour candidature {candidature.id}")
            except Exception as e:
                logger.error(f"Erreur lancement thread email: {str(e)}")
            
            # Réponse immédiate au candidat (sans attendre les emails)
            return jsonify({
                'success': True,
                'message': 'Candidature soumise avec succès ! Vous recevrez un email de confirmation.',
                'id': candidature.id,
                'nom': candidature.nom_complet,
                'temps_traitement': f"{processing_time:.2f}s",
                'file_status': file_status
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la soumission: {str(e)}", exc_info=True)
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Une erreur est survenue: {str(e)}'}), 500
    
    @app.route('/confirmation')
    def confirmation():
        """Page de confirmation après soumission"""
        return render_template('confirmation.html')
    
    # Route publique pour la santé
    @app.route('/health')
    def health():
        """Endpoint de santé pour monitoring"""
        return jsonify({
            'status': 'healthy', 
            'timestamp': datetime.now().isoformat(),
            'candidatures_count': Candidature.query.count()
        })
    
    # Gestion des erreurs
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Erreur 500: {str(e)}")
        return render_template('errors/500.html'), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)