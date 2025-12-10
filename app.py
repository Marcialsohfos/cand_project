import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
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
    
    # Routes
    @app.route('/')
    def index():
        """Page principale du formulaire"""
        return render_template('index.html')
    
    @app.route('/postuler', methods=['POST'])
    def postuler():
        """Soumettre une candidature"""
        try:
            # Récupérer les données du formulaire
            candidature = Candidature()
            
            # Informations personnelles
            candidature.nom_complet = request.form.get('nom_complet')
            candidature.email = request.form.get('email')
            candidature.telephone = request.form.get('telephone')
            candidature.ville = request.form.get('ville')
            candidature.portfolio_lien = request.form.get('portfolio_lien')
            candidature.lettre_motivation_text = request.form.get('motivation')
            candidature.competences_marketing = request.form.get('competences')
            
            # Validation
            if not candidature.nom_complet or not candidature.email:
                return jsonify({'success': False, 'error': 'Nom et email sont obligatoires'}), 400
            
            # Traiter les fichiers
            fichiers = {}
            for field in ['cv', 'portfolio_fichier', 'lettre_motivation']:
                if field in request.files:
                    file = request.files[field]
                    if file and file.filename:
                        filename = save_file(file, candidature.nom_complet, field)
                        if filename:
                            setattr(candidature, field + '_path', filename)
            
            # Sauvegarder en base de données
            db.session.add(candidature)
            db.session.commit()
            
            # Envoyer l'email de confirmation
            send_confirmation_email(candidature)
            
            # Envoyer la notification à l'admin
            send_admin_notification(candidature)
            
            return jsonify({
                'success': True,
                'message': 'Candidature soumise avec succès !',
                'id': candidature.id,
                'nom': candidature.nom_complet
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la soumission: {str(e)}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/admin/candidatures')
    def liste_candidatures():
        """Page admin pour voir les candidatures (protéger cette route en production)"""
        # En production, ajouter une authentification
        candidatures = Candidature.query.order_by(Candidature.date_soumission.desc()).all()
        return render_template('admin_candidatures.html', candidatures=candidatures)
    
    @app.route('/admin/candidature/<int:id>')
    def voir_candidature(id):
        """Voir les détails d'une candidature"""
        candidature = Candidature.query.get_or_404(id)
        return render_template('admin_candidature_detail.html', candidature=candidature)
    
    @app.route('/admin/download/<int:id>/<string:document>')
    def download_document(id, document):
        """Télécharger un document spécifique"""
        candidature = Candidature.query.get_or_404(id)
        
        if document == 'cv' and candidature.cv_path:
            return send_file(
                os.path.join(app.config['UPLOAD_FOLDER'], candidature.cv_path),
                as_attachment=True,
                download_name=f"CV_{candidature.nom_complet}.pdf"
            )
        elif document == 'lettre_motivation' and candidature.lettre_motivation_path:
            return send_file(
                os.path.join(app.config['UPLOAD_FOLDER'], candidature.lettre_motivation_path),
                as_attachment=True
            )
        elif document == 'portfolio' and candidature.portfolio_fichier_path:
            return send_file(
                os.path.join(app.config['UPLOAD_FOLDER'], candidature.portfolio_fichier_path),
                as_attachment=True
            )
        
        return jsonify({'error': 'Document non trouvé'}), 404
    
    @app.route('/admin/download-all/<int:id>')
    def download_all_documents(id):
        """Télécharger tous les documents d'une candidature en ZIP"""
        import zipfile
        from io import BytesIO
        
        candidature = Candidature.query.get_or_404(id)
        
        # Créer un fichier ZIP en mémoire
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Ajouter chaque document au ZIP
            documents = [
                ('cv', candidature.cv_path),
                ('lettre_motivation', candidature.lettre_motivation_path),
                ('portfolio', candidature.portfolio_fichier_path)
            ]
            
            for doc_type, path in documents:
                if path:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
                    if os.path.exists(file_path):
                        zf.write(file_path, f"{candidature.nom_complet}_{doc_type}_{os.path.basename(path)}")
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            download_name=f"Candidature_{candidature.nom_complet}_{candidature.id}.zip",
            as_attachment=True,
            mimetype='application/zip'
        )
    
    @app.route('/api/candidatures')
    def api_candidatures():
        """API pour récupérer les candidatures (pour dashboard)"""
        candidatures = Candidature.query.order_by(Candidature.date_soumission.desc()).all()
        
        result = []
        for c in candidatures:
            result.append({
                'id': c.id,
                'nom_complet': c.nom_complet,
                'email': c.email,
                'ville': c.ville,
                'date_soumission': c.date_soumission.isoformat(),
                'statut': c.statut,
                'has_cv': bool(c.cv_path),
                'has_lettre': bool(c.lettre_motivation_path),
                'has_portfolio': bool(c.portfolio_fichier_path)
            })
        
        return jsonify(result)
    
    @app.route('/health')
    def health():
        """Endpoint de santé pour monitoring"""
        return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
    
    return app


def save_file(file, nom_candidat, type_document):
    """Sauvegarder un fichier uploadé"""
    if file and file.filename:
        # Sécuriser le nom du fichier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_name = secure_filename(file.filename)
        extension = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
        
        # Nom du fichier
        nom_simplifie = nom_candidat.replace(' ', '_').replace("'", "").replace('"', '')
        new_filename = f"{timestamp}_{nom_simplifie}_{type_document}.{extension}"
        
        # Chemin complet
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
        
        # Sauvegarder
        file.save(filepath)
        
        logger.info(f"Fichier sauvegardé: {new_filename}")
        return new_filename
    
    return None


def send_confirmation_email(candidature):
    """Envoyer un email de confirmation au candidat"""
    try:
        msg = Message(
            subject="Confirmation de réception de votre candidature - SCSM SARL",
            recipients=[candidature.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.body = f"""
        Bonjour {candidature.nom_complet},
        
        Nous accusons réception de votre candidature pour le poste chez SCSM SARL.
        
        Détails de votre soumission:
        - Date: {candidature.date_soumission.strftime('%d/%m/%Y %H:%M')}
        - Référence: CAND{candidature.id:06d}
        
        Nous examinerons votre dossier avec attention et vous contacterons si votre profil retient notre attention.
        
        Date limite de candidature: {current_app.config['DATE_LIMITE'].strftime('%d/%m/%Y')}
        
        Pour toute question, contactez-nous à:
        - Email: {current_app.config['EMAIL_CONTACT']}
        - Support: {current_app.config['EMAIL_SUPPORT']}
        
        Cordialement,
        L'équipe de recrutement SCSM SARL
        https://scsmaubmar.org/
        """
        
        mail.send(msg)
        logger.info(f"Email de confirmation envoyé à {candidature.email}")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")


def send_admin_notification(candidature):
    """Notifier l'admin de la nouvelle candidature"""
    try:
        msg = Message(
            subject=f"[SCSM] Nouvelle candidature: {candidature.nom_complet}",
            recipients=[current_app.config['EMAIL_CONTACT']],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.body = f"""
        Nouvelle candidature reçue:
        
        Candidat: {candidature.nom_complet}
        Email: {candidature.email}
        Téléphone: {candidature.telephone}
        Ville: {candidature.ville}
        Date: {candidature.date_soumission.strftime('%d/%m/%Y %H:%M')}
        ID: CAND{candidature.id:06d}
        
        Pour voir les détails: {url_for('voir_candidature', id=candidature.id, _external=True)}
        Liste complète: {url_for('liste_candidatures', _external=True)}
        """
        
        mail.send(msg)
        logger.info(f"Notification admin envoyée pour candidature {candidature.id}")
        
    except Exception as e:
        logger.error(f"Erreur notification admin: {str(e)}")


# Import tardif pour éviter les imports circulaires
from flask import current_app

# Créer l'application
app = create_app()

#if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=5000)
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)