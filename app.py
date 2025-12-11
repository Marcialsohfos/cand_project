import os
import json
import zipfile
from datetime import datetime
from io import BytesIO
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_file, url_for, flash, redirect, session, abort, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from config import config
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation des extensions
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()

# Modèle Candidature
class Candidature(db.Model):
    __tablename__ = 'candidatures'
    
    id = db.Column(db.Integer, primary_key=True)
    # Informations personnelles
    nom_complet = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telephone = db.Column(db.String(20))
    ville = db.Column(db.String(100))
    portfolio_lien = db.Column(db.String(500))
    
    # Documents (chemins de fichiers)
    cv_path = db.Column(db.String(500))
    lettre_motivation_path = db.Column(db.String(500))
    lettre_motivation_text = db.Column(db.Text)
    portfolio_fichier_path = db.Column(db.String(500))
    
    # Informations supplémentaires
    competences_marketing = db.Column(db.Text)
    
    # Métadonnées
    date_soumission = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(50), default='Nouvelle')  # Nouvelle, En revue, Contacté, Rejeté
    notes_admin = db.Column(db.Text)
    
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
            'has_portfolio': bool(self.portfolio_fichier_path)
        }


# Décorateur pour protéger les routes admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def create_app(config_name='default'):
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Charger la configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
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
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    
    def save_file(file, nom_candidat, type_document):
        """Sauvegarder un fichier uploadé"""
        if file and file.filename and allowed_file(file.filename):
            # Sécuriser le nom du fichier
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            original_name = secure_filename(file.filename)
            extension = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
            
            # Nom du fichier
            nom_simplifie = ''.join(c for c in nom_candidat if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_')
            new_filename = f"{timestamp}_{nom_simplifie}_{type_document}.{extension}"
            
            # Chemin complet
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            
            # Sauvegarder
            file.save(filepath)
            
            logger.info(f"Fichier sauvegardé: {new_filename}")
            return new_filename
        
        return None
    
    # Routes publiques (candidats)
    @app.route('/')
    def index():
        """Page principale du formulaire"""
        date_limite = app.config['DATE_LIMITE']
        aujourdhui = datetime.now().date()
        accepte_candidatures = aujourdhui <= date_limite
        
        return render_template('index.html', 
                             accepte_candidatures=accepte_candidatures,
                             date_limite=date_limite)
    
    @app.route('/postuler', methods=['POST'])
    def postuler():
        """Soumettre une candidature"""
        # Vérifier la date limite
        aujourdhui = datetime.now().date()
        if aujourdhui > app.config['DATE_LIMITE']:
            return jsonify({
                'success': False, 
                'error': 'La période de candidature est terminée.'
            }), 400
        
        try:
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
            
            # Validation
            if not candidature.nom_complet:
                return jsonify({'success': False, 'error': 'Le nom complet est obligatoire'}), 400
            
            if not candidature.email:
                return jsonify({'success': False, 'error': 'L\'email est obligatoire'}), 400
            
            # Traiter les fichiers
            if 'cv' in request.files:
                file = request.files['cv']
                if file and file.filename:
                    filename = save_file(file, candidature.nom_complet, 'cv')
                    if filename:
                        candidature.cv_path = filename
            
            if 'lettre_motivation' in request.files:
                file = request.files['lettre_motivation']
                if file and file.filename:
                    filename = save_file(file, candidature.nom_complet, 'lettre_motivation')
                    if filename:
                        candidature.lettre_motivation_path = filename
            
            if 'portfolio_fichier' in request.files:
                file = request.files['portfolio_fichier']
                if file and file.filename:
                    filename = save_file(file, candidature.nom_complet, 'portfolio')
                    if filename:
                        candidature.portfolio_fichier_path = filename
            
            # Sauvegarder en base de données
            db.session.add(candidature)
            db.session.commit()
            
            # Envoyer l'email de confirmation
            send_confirmation_email(candidature, app)
            
            # Envoyer la notification à l'admin
            send_admin_notification(candidature, app)
            
            return jsonify({
                'success': True,
                'message': 'Candidature soumise avec succès !',
                'id': candidature.id,
                'nom': candidature.nom_complet
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la soumission: {str(e)}")
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Une erreur est survenue. Veuillez réessayer.'}), 500
    
    @app.route('/confirmation')
    def confirmation():
        """Page de confirmation après soumission"""
        return render_template('confirmation.html')
    
    # Routes d'authentification admin
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        """Page de connexion admin"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Vérifier les identifiants
            if (username == app.config['ADMIN_USERNAME'] and 
                check_password_hash(app.config.get('ADMIN_PASSWORD_HASH', ''), password)):
                
                session['admin_logged_in'] = True
                session.permanent = True
                flash('Connexion réussie!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Identifiants incorrects', 'error')
        
        return render_template('admin_login.html')
    
    @app.route('/admin/logout')
    def admin_logout():
        """Déconnexion admin"""
        session.pop('admin_logged_in', None)
        flash('Vous avez été déconnecté', 'info')
        return redirect(url_for('admin_login'))
    
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
        
        return render_template('admin_dashboard.html', 
                             stats=stats, 
                             candidatures=recent_candidatures)
    
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
        ).paginate(page=page, per_page=per_page)
        
        return render_template('admin_candidatures.html', 
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
        
        return render_template('admin_candidature_detail.html', 
                             candidature=candidature)
    
    @app.route('/admin/download/<int:id>/<string:document>')
    @admin_required
    def download_document(id, document):
        """Télécharger un document spécifique"""
        candidature = Candidature.query.get_or_404(id)
        
        if document == 'cv' and candidature.cv_path:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], candidature.cv_path)
            if os.path.exists(filepath):
                return send_file(
                    filepath,
                    as_attachment=True,
                    download_name=f"CV_{candidature.nom_complet}_{id}.{candidature.cv_path.split('.')[-1]}"
                )
        
        elif document == 'lettre_motivation' and candidature.lettre_motivation_path:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], candidature.lettre_motivation_path)
            if os.path.exists(filepath):
                return send_file(
                    filepath,
                    as_attachment=True,
                    download_name=f"Lettre_{candidature.nom_complet}_{id}.{candidature.lettre_motivation_path.split('.')[-1]}"
                )
        
        elif document == 'portfolio' and candidature.portfolio_fichier_path:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], candidature.portfolio_fichier_path)
            if os.path.exists(filepath):
                return send_file(
                    filepath,
                    as_attachment=True,
                    download_name=f"Portfolio_{candidature.nom_complet}_{id}.{candidature.portfolio_fichier_path.split('.')[-1]}"
                )
        
        flash('Document non trouvé', 'error')
        return redirect(url_for('voir_candidature', id=id))
    
    @app.route('/admin/download-all/<int:id>')
    @admin_required
    def download_all_documents(id):
        """Télécharger tous les documents d'une candidature en ZIP"""
        candidature = Candidature.query.get_or_404(id)
        
        # Créer un fichier ZIP en mémoire
        memory_file = BytesIO()
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            documents = [
                ('cv', candidature.cv_path),
                ('lettre_motivation', candidature.lettre_motivation_path),
                ('portfolio', candidature.portfolio_fichier_path)
            ]
            
            for doc_type, path in documents:
                if path:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
                    if os.path.exists(file_path):
                        extension = path.split('.')[-1]
                        zf.write(file_path, f"{candidature.nom_complet}_{doc_type}.{extension}")
            
            # Ajouter un fichier texte avec les informations
            info_content = f"""
            Candidature: {candidature.nom_complet}
            Email: {candidature.email}
            Téléphone: {candidature.telephone}
            Ville: {candidature.ville}
            Date de soumission: {candidature.date_soumission}
            Statut: {candidature.statut}
            
            Lettre de motivation:
            {candidature.lettre_motivation_text}
            
            Compétences:
            {candidature.competences_marketing}
            
            Portfolio (lien): {candidature.portfolio_lien}
            """
            
            zf.writestr(f"{candidature.nom_complet}_informations.txt", info_content)
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            download_name=f"Candidature_{candidature.nom_complet}_{id}.zip",
            as_attachment=True,
            mimetype='application/zip'
        )
    
    @app.route('/admin/api/candidatures')
    @admin_required
    def api_candidatures():
        """API pour récupérer les candidatures (pour dashboard)"""
        candidatures = Candidature.query.order_by(Candidature.date_soumission.desc()).all()
        return jsonify([c.to_dict() for c in candidatures])
    
    @app.route('/admin/statistiques')
    @admin_required
    def statistiques():
        """Page de statistiques"""
        # Statistiques par statut
        stats_statut = db.session.query(
            Candidature.statut, 
            db.func.count(Candidature.id)
        ).group_by(Candidature.statut).all()
        
        # Statistiques par mois
        stats_mois = db.session.query(
            db.func.strftime('%Y-%m', Candidature.date_soumission),
            db.func.count(Candidature.id)
        ).group_by(db.func.strftime('%Y-%m', Candidature.date_soumission)).all()
        
        # Top villes
        top_villes = db.session.query(
            Candidature.ville,
            db.func.count(Candidature.id)
        ).filter(Candidature.ville.isnot(None)).group_by(Candidature.ville).order_by(
            db.func.count(Candidature.id).desc()
        ).limit(10).all()
        
        return render_template('admin_statistiques.html',
                             stats_statut=stats_statut,
                             stats_mois=stats_mois,
                             top_villes=top_villes)
    
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
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Erreur 500: {str(e)}")
        return render_template('500.html'), 500
    
    return app


def send_confirmation_email(candidature, app):
    """Envoyer un email de confirmation au candidat"""
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
        - Email: {app.config['EMAIL_CONTACT']}
        - Support: {app.config['EMAIL_SUPPORT']}
        
        Cordialement,
        L'équipe de recrutement SCSM SARL
        """
        
        mail.send(msg)
        logger.info(f"Email de confirmation envoyé à {candidature.email}")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de confirmation: {str(e)}")


def send_admin_notification(candidature, app):
    """Notifier l'admin de la nouvelle candidature"""
    try:
        msg = Message(
            subject=f"[SCSM] Nouvelle candidature: {candidature.nom_complet}",
            recipients=[app.config['EMAIL_CONTACT']],
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


# Script pour générer un hash de mot de passe admin
def create_admin_password():
    """Utilitaire pour créer un hash de mot de passe"""
    from werkzeug.security import generate_password_hash
    password = input("Entrez le mot de passe admin: ")
    print(f"HASH généré: {generate_password_hash(password)}")


if __name__ == '__main__':
    app = create_app()
    
    # Pour générer un hash de mot de passe
    # if len(sys.argv) > 1 and sys.argv[1] == 'create-password':
    #     create_admin_password()
    # else:
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)