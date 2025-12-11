<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Postuler - SCSM SARL</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
    <!-- Bootstrap CSS pour les spinners -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <meta name="description" content="Formulaire de candidature en ligne pour SCSM SARL - Date limite: 31 décembre 2025">
    <style>
        /* Styles supplémentaires pour l'upload */
        .file-name-display {
            font-size: 0.9em;
            padding: 8px 12px;
            background-color: #d4edda;
            border-radius: 4px;
            border-left: 4px solid #28a745;
            margin-top: 5px;
            color: #155724;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .file-name-display i {
            color: #28a745;
        }
        
        .upload-success {
            border-color: #28a745;
            background-color: #d4edda;
        }
        
        .upload-error {
            border-color: #dc3545;
            background-color: #f8d7da;
            color: #721c24;
        }
        
        .upload-warning {
            border-color: #ffc107;
            background-color: #fff3cd;
            color: #856404;
        }
        
        .spinner-border {
            margin-right: 8px;
            vertical-align: middle;
        }
        
        /* Navigation */
        .admin-nav {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
        }
        
        .admin-nav a {
            background: #343a40;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .admin-nav a:hover {
            background: #495057;
        }
        
        /* Drag and drop styles */
        .upload-zone {
            position: relative;
            border: 2px dashed #ccc;
            border-radius: 8px;
            padding: 40px 20px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            background-color: #f8f9fa;
        }
        
        .upload-zone:hover {
            border-color: #007bff;
            background-color: #e9ecef;
        }
        
        .upload-zone.dragover {
            border-color: #28a745;
            background-color: #d4edda;
        }
        
        .upload-zone input[type="file"] {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            cursor: pointer;
        }
        
        .upload-content i {
            font-size: 48px;
            color: #6c757d;
            margin-bottom: 10px;
        }
        
        .upload-content p {
            color: #6c757d;
            margin: 0;
        }
        
        .upload-content span {
            color: #007bff;
            font-weight: 600;
        }
        
        /* Tabs for portfolio */
        .option-tabs {
            display: flex;
            margin-bottom: 15px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .tab-btn {
            padding: 10px 20px;
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-weight: 500;
            color: #6c757d;
        }
        
        .tab-btn.active {
            color: #007bff;
            border-bottom-color: #007bff;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Progress bar */
        .progress-bar-container {
            height: 6px;
            background-color: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .progress-bar {
            height: 100%;
            background-color: #007bff;
            width: 0%;
            transition: width 0.3s;
        }
        
        .progress-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <!-- Navigation admin -->
    <div class="admin-nav">
        <a href="{{ url_for('home') }}">
            <i class="fas fa-home"></i> Accueil
        </a>
    </div>
    
    <div class="container">
        <!-- En-tête avec logo -->
        <header class="header">
            <div class="logo-container">
                <h1><i class="fas fa-briefcase"></i> SCSM SARL</h1>
                <p class="tagline">Excellence, Innovation & Impact</p>
            </div>
            
            <div class="deadline-container">
                <div class="deadline-card">
                    <i class="fas fa-calendar-alt"></i>
                    <div>
                        <strong>Date limite</strong>
                        <p>{{ date_limite.strftime('%d/%m/%Y') }}</p>
                    </div>
                </div>
                <div class="counter-card" id="counter">
                    <i class="fas fa-clock"></i>
                    <div>
                        <strong>Temps restant</strong>
                        <p id="countdown">Chargement...</p>
                    </div>
                </div>
            </div>
        </header>

        <!-- Bannière d'information -->
        <div class="info-banner">
            <i class="fas fa-info-circle"></i>
            <p>Lien de candidature : <strong id="current-url"></strong></p>
            <button class="btn-copy" onclick="copyLink()">
                <i class="fas fa-copy"></i> Copier le lien
            </button>
        </div>

        <!-- Contenu principal -->
        <main class="main-grid">
            <!-- Formulaire -->
            <div class="form-section">
                <div class="form-header">
                    <h2><i class="fas fa-file-signature"></i> Formulaire de Candidature</h2>
                    <p class="form-subtitle">Remplissez soigneusement tous les champs obligatoires (*)</p>
                    {% if not accepte_candidatures %}
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle"></i> 
                        La période de candidature est terminée. Vous pouvez toujours remplir le formulaire pour tester.
                    </div>
                    {% endif %}
                </div>

                <form id="candidatureForm" enctype="multipart/form-data">
                    <!-- Section 1: Informations personnelles -->
                    <fieldset class="form-fieldset">
                        <legend><i class="fas fa-user-circle"></i> Informations Personnelles</legend>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="nom_complet">
                                    <i class="fas fa-user"></i> Nom complet *
                                </label>
                                <input type="text" id="nom_complet" name="nom_complet" 
                                       placeholder="Votre nom et prénom" required>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="email">
                                    <i class="fas fa-envelope"></i> Adresse email *
                                </label>
                                <input type="email" id="email" name="email" 
                                       placeholder="exemple@email.com" required>
                                <div class="validation-message" id="email-validation"></div>
                            </div>
                            
                            <div class="form-group">
                                <label for="telephone">
                                    <i class="fas fa-phone"></i> Téléphone
                                </label>
                                <input type="tel" id="telephone" name="telephone" 
                                       placeholder="+237 XXX XXX XXX">
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="ville">
                                    <i class="fas fa-map-marker-alt"></i> Ville de résidence *
                                </label>
                                <select id="ville" name="ville" required>
                                    <option value="">Sélectionnez votre ville</option>
                                    <option value="Bertoua">Bertoua</option>
                                    <option value="Yaoundé">Yaoundé</option>
                                    <option value="Bafoussam">Bafoussam</option>
                                    <option value="Douala">Douala</option>
                                    <option value="Autre">Autre ville</option>
                                </select>
                                <p class="form-note">Possibilité de négociation pour les candidatures hors Bertoua</p>
                            </div>
                        </div>
                    </fieldset>

                    <!-- Section 2: Documents -->
                    <fieldset class="form-fieldset">
                        <legend><i class="fas fa-paperclip"></i> Documents Requis</legend>
                        
                        <!-- CV -->
                        <div class="document-upload">
                            <div class="document-header">
                                <i class="fas fa-file-contract"></i>
                                <div>
                                    <h4>Curriculum Vitae (CV) *</h4>
                                    <p>Format: PDF, DOC, DOCX (max 20MB)</p>
                                </div>
                            </div>
                            <div class="upload-zone" id="cv-zone">
                                <input type="file" id="cv" name="cv" accept=".pdf,.doc,.docx" required>
                                <div class="upload-content">
                                    <i class="fas fa-cloud-upload-alt"></i>
                                    <p>Glissez-déposez votre CV ou <span>parcourir</span></p>
                                </div>
                            </div>
                            <div class="file-status" id="cv-status"></div>
                        </div>

                        <!-- Portfolio -->
                        <div class="document-upload">
                            <div class="document-header">
                                <i class="fas fa-briefcase"></i>
                                <div>
                                    <h4>Portfolio</h4>
                                    <p>Lien en ligne ou fichier (PDF, images, max 20MB)</p>
                                </div>
                            </div>
                            
                            <div class="portfolio-options">
                                <div class="option-tabs">
                                    <button type="button" class="tab-btn active" data-tab="lien">Lien en ligne</button>
                                    <button type="button" class="tab-btn" data-tab="fichier">Fichier</button>
                                </div>
                                
                                <div class="tab-content active" id="lien-tab">
                                    <input type="url" id="portfolio_lien" name="portfolio_lien" 
                                           placeholder="https://votre-portfolio.com">
                                </div>
                                
                                <div class="tab-content" id="fichier-tab">
                                    <div class="upload-zone" id="portfolio-zone">
                                        <input type="file" id="portfolio_fichier" name="portfolio_fichier" 
                                               accept=".pdf,.jpg,.jpeg,.png,.gif">
                                        <div class="upload-content">
                                            <i class="fas fa-cloud-upload-alt"></i>
                                            <p>Glissez-déposez votre portfolio ou <span>parcourir</span></p>
                                        </div>
                                    </div>
                                    <div class="file-status" id="portfolio-status"></div>
                                </div>
                            </div>
                        </div>

                        <!-- Lettre de motivation -->
                        <div class="document-upload">
                            <div class="document-header">
                                <i class="fas fa-envelope-open-text"></i>
                                <div>
                                    <h4>Lettre de motivation *</h4>
                                    <p>Format: PDF, DOC, DOCX, TXT (max 20MB)</p>
                                </div>
                            </div>
                            <div class="upload-zone" id="lettre-zone">
                                <input type="file" id="lettre_motivation" name="lettre_motivation" 
                                       accept=".pdf,.doc,.docx,.txt" required>
                                <div class="upload-content">
                                    <i class="fas fa-cloud-upload-alt"></i>
                                    <p>Glissez-déposez votre lettre ou <span>parcourir</span></p>
                                </div>
                            </div>
                            <div class="file-status" id="lettre-status"></div>
                        </div>
                    </fieldset>

                    <!-- Section 3: Contenu -->
                    <fieldset class="form-fieldset">
                        <legend><i class="fas fa-edit"></i> Contenu de la Candidature</legend>
                        
                        <div class="form-group">
                            <label for="motivation">
                                <i class="fas fa-comment-dots"></i> Lettre de motivation (texte) *
                                <span class="sub-label">Expliquez votre intérêt pour SCSM SARL et ses thématiques</span>
                            </label>
                            <textarea id="motivation" name="motivation" rows="8" required 
                                      placeholder="Cher(e) Responsable des Ressources Humaines,

Je souhaite exprimer mon vif intérêt pour le poste chez SCSM SARL...

..."></textarea>
                            <div class="char-count">
                                <span id="motivation-chars">0</span> / 2000 caractères
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="competences">
                                <i class="fas fa-chart-line"></i> Compétences en marketing digital
                                <span class="sub-label">Décrivez vos compétences, outils maîtrisés, expériences</span>
                            </label>
                            <textarea id="competences" name="competences" rows="6"
                                      placeholder="• Gestion des réseaux sociaux
• SEO/SEA
• Analyse Google Analytics
• Création de contenu
• Email marketing
• ..."></textarea>
                            <div class="char-count">
                                <span id="competences-chars">0</span> / 1000 caractères
                            </div>
                        </div>
                    </fieldset>

                    <!-- Informations de contact -->
                    <div class="contact-card">
                        <h3><i class="fas fa-address-book"></i> Contacts SCSM SARL</h3>
                        <div class="contact-links">
                            <a href="https://scsmaubmar.org/" target="_blank" class="contact-link">
                                <i class="fas fa-globe"></i>
                                <span>https://scsmaubmar.org/</span>
                            </a>
                            <a href="mailto:scsmaubma@gmail.com" class="contact-link">
                                <i class="fas fa-envelope"></i>
                                <span>scsmaubma@gmail.com</span>
                            </a>
                            <a href="mailto:support@scsmaubmar.org" class="contact-link">
                                <i class="fas fa-headset"></i>
                                <span>support@scsmaubmar.org</span>
                            </a>
                        </div>
                    </div>

                    <!-- Note finale -->
                    <div class="final-note">
                        <h4><i class="fas fa-star"></i> Note Finale</h4>
                        <p>Nous cherchons un(e) professionnel(le) capable de traduire visuellement l'excellence, l'innovation et l'impact de SCSM SARL, en alliant rigueur scientifique et attractivité marketing.</p>
                        <p class="highlight-note">Si vous êtes créatif(ve), passionné(e) par les données et les défis visuels, cette offre est pour vous !</p>
                        <p class="advantage-note">
                            <i class="fas fa-plus-circle"></i> 
                            <strong>Atout:</strong> Avoir des compétences en marketing digital serait un atout.
                        </p>
                    </div>

                    <!-- Confidentialité et soumission -->
                    <div class="privacy-section">
                        <div class="privacy-agreement">
                            <input type="checkbox" id="privacy" name="privacy" required>
                            <label for="privacy">
                                J'accepte que mes données soient traitées dans le cadre du processus de recrutement, conformément à la politique de confidentialité de SCSM SARL.
                            </label>
                        </div>
                        
                        <div class="form-actions">
                            <button type="button" id="resetBtn" class="btn-secondary">
                                <i class="fas fa-redo"></i> Réinitialiser
                            </button>
                            <button type="button" id="previewBtn" class="btn-secondary">
                                <i class="fas fa-eye"></i> Prévisualiser
                            </button>
                            <button type="submit" id="submitBtn" class="btn-primary">
                                <i class="fas fa-paper-plane"></i> Soumettre ma candidature
                            </button>
                        </div>

                        <div class="progress-section" id="progressSection" style="display: none;">
                            <div class="progress-info">
                                <span id="progressText">Envoi en cours...</span>
                                <span id="progressPercent">0%</span>
                            </div>
                            <div class="progress-bar-container">
                                <div class="progress-bar" id="progressBar"></div>
                            </div>
                        </div>
                    </div>
                </form>
            </div>

            <!-- Sidebar -->
            <aside class="sidebar">
                <!-- Navigation rapide -->
                <div class="info-card">
                    <h3><i class="fas fa-rocket"></i> Navigation Rapide</h3>
                    <div class="quick-links">
                        <a href="{{ url_for('home') }}" class="quick-link">
                            <i class="fas fa-home"></i> Page d'accueil
                        </a>
                        <a href="{{ url_for('contact') }}" class="quick-link">
                            <i class="fas fa-envelope"></i> Contact
                        </a>
                        <a href="/admin/login" class="quick-link">
                            <i class="fas fa-lock"></i> Espace Admin
                        </a>
                        <a href="/test-upload" class="quick-link">
                            <i class="fas fa-upload"></i> Test Upload
                        </a>
                    </div>
                </div>

                <!-- Statistiques -->
                <div class="stats-card">
                    <h3><i class="fas fa-chart-bar"></i> Statistiques</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value" id="total-candidatures">--</div>
                            <div class="stat-label">Candidatures</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="jours-restants">--</div>
                            <div class="stat-label">Jours restants</div>
                        </div>
                    </div>
                </div>

                <!-- Informations importantes -->
                <div class="info-card">
                    <h3><i class="fas fa-map-pin"></i> Lieu de travail</h3>
                    <p><strong>Siège social:</strong> Bertoua</p>
                    <p><strong>Déplacements possibles:</strong> Yaoundé et Bafoussam</p>
                    <div class="highlight-box">
                        <i class="fas fa-comments"></i>
                        <p>Négociation possible pour les candidatures provenant de Yaoundé et autres villes</p>
                    </div>
                </div>

                <!-- Format acceptés -->
                <div class="info-card">
                    <h3><i class="fas fa-file-check"></i> Formats acceptés</h3>
                    <ul class="format-list">
                        <li><i class="fas fa-file-pdf"></i> PDF (.pdf)</li>
                        <li><i class="fas fa-file-word"></i> Word (.doc, .docx)</li>
                        <li><i class="fas fa-file-alt"></i> Texte (.txt)</li>
                        <li><i class="fas fa-file-image"></i> Images (.jpg, .png, .gif)</li>
                    </ul>
                </div>

                <!-- Guide -->
                <div class="info-card">
                    <h3><i class="fas fa-lightbulb"></i> Conseils</h3>
                    <ol class="tips-list">
                        <li>Vérifiez vos informations avant soumission</li>
                        <li>Taille maximale par fichier: 20MB</li>
                        <li>Vous recevrez un email de confirmation</li>
                        <li>Gardez une copie de vos documents</li>
                    </ol>
                </div>

                <!-- Partage -->
                <div class="share-card">
                    <h3><i class="fas fa-share-alt"></i> Partager</h3>
                    <div class="share-buttons">
                        <button class="share-btn" onclick="shareOnWhatsApp()">
                            <i class="fab fa-whatsapp"></i>
                        </button>
                        <button class="share-btn" onclick="shareOnLinkedIn()">
                            <i class="fab fa-linkedin"></i>
                        </button>
                        <button class="share-btn" onclick="shareByEmail()">
                            <i class="fas fa-envelope"></i>
                        </button>
                        <button class="share-btn" onclick="copyShareLink()">
                            <i class="fas fa-link"></i>
                        </button>
                    </div>
                </div>
            </aside>
        </main>

        <!-- Footer -->
        <footer class="footer">
            <div class="footer-content">
                <div class="footer-logo">
                    <h3><i class="fas fa-briefcase"></i> SCSM SARL</h3>
                    <p>Excellence, Innovation & Impact</p>
                </div>
                
                <div class="footer-links">
                    <a href="https://scsmaubmar.org/" target="_blank">
                        <i class="fas fa-external-link-alt"></i> Site officiel
                    </a>
                    <a href="mailto:support@scsmaubmar.org">
                        <i class="fas fa-question-circle"></i> Support technique
                    </a>
                    <a href="/admin/login">
                        <i class="fas fa-lock"></i> Admin
                    </a>
                </div>
                
                <div class="footer-copyright">
                    <p>© 2024 SCSM SARL. Tous droits réservés.</p>
                    <p class="footer-note">Formulaire de candidature en ligne v2.0</p>
                </div>
            </div>
        </footer>
    </div>

    <!-- Modals -->
    <div id="successModal" class="modal">
        <div class="modal-content">
            <div class="modal-success">
                <i class="fas fa-check-circle"></i>
                <h2>Candidature soumise avec succès !</h2>
                <p id="successMessage">Merci pour votre candidature. Vous allez recevoir un email de confirmation.</p>
                <div id="fileDetails" class="file-details"></div>
                <div class="modal-actions">
                    <button class="btn-primary" onclick="closeModal('successModal')">
                        <i class="fas fa-check"></i> Compris
                    </button>
                    <button class="btn-secondary" onclick="window.location.href='{{ url_for('confirmation') }}'">
                        <i class="fas fa-eye"></i> Voir confirmation
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div id="errorModal" class="modal">
        <div class="modal-content">
            <div class="modal-error">
                <i class="fas fa-exclamation-circle"></i>
                <h2>Erreur de soumission</h2>
                <p id="errorMessage">Une erreur est survenue lors de l'envoi de votre candidature.</p>
                <div class="modal-actions">
                    <button class="btn-primary" onclick="closeModal('errorModal')">
                        <i class="fas fa-times"></i> Fermer
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div id="previewModal" class="modal">
        <div class="modal-content large">
            <div class="modal-header">
                <h2><i class="fas fa-eye"></i> Prévisualisation</h2>
                <span class="close" onclick="closeModal('previewModal')">&times;</span>
            </div>
            <div class="modal-body" id="previewContent"></div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Afficher l'URL actuelle
        document.getElementById('current-url').textContent = window.location.href;
        
        // Initialisation au chargement de la page
        document.addEventListener('DOMContentLoaded', function() {
            initializeFileUploads();
            initializePortfolioTabs();
            setupDragAndDrop();
            initializeFormValidation();
            loadStatistics();
            
            // Charger le nombre de candidatures
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    if (data.candidatures_count !== undefined) {
                        document.getElementById('total-candidatures').textContent = data.candidatures_count;
                    }
                })
                .catch(error => console.error('Erreur chargement statistiques:', error));
        });
        
        // Gestion de l'upload des fichiers
        function initializeFileUploads() {
            const fileInputs = document.querySelectorAll('input[type="file"]');
            
            fileInputs.forEach(input => {
                input.addEventListener('change', function(e) {
                    handleFileSelect(this, e);
                });
            });
        }
        
        function handleFileSelect(input, event) {
            const file = input.files[0];
            const parent = input.closest('.document-upload');
            const statusDiv = parent.querySelector('.file-status');
            
            if (!file) {
                statusDiv.innerHTML = '';
                return;
            }
            
            // Vérifier la taille (20MB max)
            const maxSize = 20 * 1024 * 1024;
            if (file.size > maxSize) {
                statusDiv.innerHTML = `
                    <div class="file-name-display upload-error">
                        <i class="fas fa-exclamation-triangle"></i>
                        Fichier trop volumineux (${(file.size / (1024*1024)).toFixed(2)} MB > 20 MB)
                    </div>
                `;
                input.value = '';
                return;
            }
            
            // Vérifier l'extension
            const allowedExtensions = ['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'];
            const extension = file.name.split('.').pop().toLowerCase();
            
            if (!allowedExtensions.includes(extension)) {
                statusDiv.innerHTML = `
                    <div class="file-name-display upload-error">
                        <i class="fas fa-exclamation-triangle"></i>
                        Extension non autorisée: .${extension}
                    </div>
                `;
                input.value = '';
                return;
            }
            
            // Afficher le succès
            statusDiv.innerHTML = `
                <div class="file-name-display upload-success">
                    <i class="fas fa-check-circle"></i>
                    ${file.name} (${(file.size / 1024).toFixed(0)} KB)
                </div>
            `;
            
            // Ajouter un effet visuel sur la zone d'upload
            const uploadZone = parent.querySelector('.upload-zone');
            uploadZone.classList.add('upload-success');
            setTimeout(() => {
                uploadZone.classList.remove('upload-success');
            }, 1000);
        }
        
        // Gestion des onglets portfolio
        function initializePortfolioTabs() {
            const tabBtns = document.querySelectorAll('.tab-btn');
            const tabContents = document.querySelectorAll('.tab-content');
            
            tabBtns.forEach(btn => {
                btn.addEventListener('click', function() {
                    const tabId = this.getAttribute('data-tab');
                    
                    // Mettre à jour les boutons
                    tabBtns.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Mettre à jour les contenus
                    tabContents.forEach(content => {
                        content.classList.remove('active');
                        if (content.id === tabId + '-tab') {
                            content.classList.add('active');
                        }
                    });
                });
            });
        }
        
        // Drag and drop
        function setupDragAndDrop() {
            const uploadZones = document.querySelectorAll('.upload-zone');
            
            uploadZones.forEach(zone => {
                zone.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    this.classList.add('dragover');
                });
                
                zone.addEventListener('dragleave', function(e) {
                    e.preventDefault();
                    this.classList.remove('dragover');
                });
                
                zone.addEventListener('drop', function(e) {
                    e.preventDefault();
                    this.classList.remove('dragover');
                    
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        const input = this.querySelector('input[type="file"]');
                        input.files = files;
                        
                        // Déclencher l'événement change
                        const event = new Event('change', { bubbles: true });
                        input.dispatchEvent(event);
                    }
                });
            });
        }
        
        // Validation du formulaire
        function initializeFormValidation() {
            const form = document.getElementById('candidatureForm');
            if (!form) return;
            
            // Validation en temps réel de l'email
            const emailInput = document.getElementById('email');
            if (emailInput) {
                emailInput.addEventListener('blur', function() {
                    const email = this.value.trim();
                    const validationDiv = document.getElementById('email-validation');
                    
                    if (email && !isValidEmail(email)) {
                        validationDiv.innerHTML = '<span style="color: #dc3545;">Email invalide</span>';
                    } else {
                        validationDiv.innerHTML = '';
                    }
                });
            }
            
            // Compteurs de caractères
            const motivationTextarea = document.getElementById('motivation');
            const competencesTextarea = document.getElementById('competences');
            
            if (motivationTextarea) {
                motivationTextarea.addEventListener('input', function() {
                    document.getElementById('motivation-chars').textContent = this.value.length;
                });
            }
            
            if (competencesTextarea) {
                competencesTextarea.addEventListener('input', function() {
                    document.getElementById('competences-chars').textContent = this.value.length;
                });
            }
            
            // Soumission du formulaire
            form.addEventListener('submit', handleFormSubmit);
            
            // Bouton de réinitialisation
            const resetBtn = document.getElementById('resetBtn');
            if (resetBtn) {
                resetBtn.addEventListener('click', function() {
                    if (confirm('Êtes-vous sûr de vouloir réinitialiser le formulaire ?')) {
                        form.reset();
                        document.querySelectorAll('.file-status').forEach(el => {
                            el.innerHTML = '';
                        });
                        // Réactiver l'onglet lien par défaut
                        document.querySelector('.tab-btn[data-tab="lien"]').click();
                    }
                });
            }
            
            // Bouton de prévisualisation
            const previewBtn = document.getElementById('previewBtn');
            if (previewBtn) {
                previewBtn.addEventListener('click', showPreview);
            }
        }
        
        function isValidEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        }
        
        function handleFormSubmit(e) {
            e.preventDefault();
            
            // Validation des fichiers obligatoires
            const cvFile = document.getElementById('cv').files[0];
            const lettreFile = document.getElementById('lettre_motivation').files[0];
            
            if (!cvFile) {
                showError('Le CV est obligatoire');
                return;
            }
            
            if (!lettreFile) {
                showError('La lettre de motivation est obligatoire');
                return;
            }
            
            // Vérifier la taille des fichiers
            const maxSize = 20 * 1024 * 1024;
            if (cvFile.size > maxSize) {
                showError('Le CV dépasse la taille maximale de 20MB');
                return;
            }
            
            if (lettreFile.size > maxSize) {
                showError('La lettre de motivation dépasse la taille maximale de 20MB');
                return;
            }
            
            // Afficher le progress bar
            const progressSection = document.getElementById('progressSection');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            const progressPercent = document.getElementById('progressPercent');
            
            progressSection.style.display = 'block';
            progressBar.style.width = '10%';
            progressPercent.textContent = '10%';
            progressText.textContent = 'Préparation de l\'envoi...';
            
            // Désactiver le bouton de soumission
            const submitBtn = document.getElementById('submitBtn');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Envoi en cours...';
            submitBtn.disabled = true;
            
            // Créer FormData
            const formData = new FormData(this);
            
            // Mise à jour de la progression
            progressBar.style.width = '30%';
            progressPercent.textContent = '30%';
            progressText.textContent = 'Envoi des données...';
            
            // Envoyer la requête
            fetch('/postuler', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                progressBar.style.width = '60%';
                progressPercent.textContent = '60%';
                progressText.textContent = 'Traitement en cours...';
                return response.json();
            })
            .then(data => {
                progressBar.style.width = '100%';
                progressPercent.textContent = '100%';
                progressText.textContent = 'Terminé !';
                
                setTimeout(() => {
                    if (data.success) {
                        // Afficher le message de succès avec détails
                        const successMessage = document.getElementById('successMessage');
                        const fileDetails = document.getElementById('fileDetails');
                        
                        successMessage.textContent = data.message.split('\n')[0];
                        
                        if (data.file_status) {
                            let fileDetailsHTML = '<h4>Détails des fichiers:</h4><ul>';
                            for (const [doc, status] of Object.entries(data.file_status)) {
                                fileDetailsHTML += `<li>${status}</li>`;
                            }
                            fileDetailsHTML += '</ul>';
                            fileDetails.innerHTML = fileDetailsHTML;
                        }
                        
                        // Afficher la modal de succès
                        showModal('successModal');
                        
                        // Réinitialiser le formulaire après 3 secondes
                        setTimeout(() => {
                            document.getElementById('candidatureForm').reset();
                            document.querySelectorAll('.file-status').forEach(el => {
                                el.innerHTML = '';
                            });
                            progressSection.style.display = 'none';
                            progressBar.style.width = '0%';
                        }, 3000);
                        
                    } else {
                        // Afficher l'erreur
                        document.getElementById('errorMessage').textContent = data.error;
                        showModal('errorModal');
                    }
                }, 500);
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('errorMessage').textContent = 'Une erreur réseau est survenue. Veuillez réessayer.';
                showModal('errorModal');
            })
            .finally(() => {
                // Restaurer le bouton
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                    progressSection.style.display = 'none';
                    progressBar.style.width = '0%';
                }, 2000);
            });
        }
        
        function showError(message) {
            document.getElementById('errorMessage').textContent = message;
            showModal('errorModal');
        }
        
        function showPreview() {
            const form = document.getElementById('candidatureForm');
            const previewContent = document.getElementById('previewContent');
            
            let html = '<div class="preview-content">';
            html += '<h3>Prévisualisation de votre candidature</h3>';
            
            // Informations personnelles
            html += '<h4>Informations personnelles:</h4>';
            html += '<ul>';
            html += `<li><strong>Nom complet:</strong> ${form.nom_complet.value}</li>`;
            html += `<li><strong>Email:</strong> ${form.email.value}</li>`;
            html += `<li><strong>Téléphone:</strong> ${form.telephone.value || 'Non renseigné'}</li>`;
            html += `<li><strong>Ville:</strong> ${form.ville.value}</li>`;
            html += '</ul>';
            
            // Documents
            html += '<h4>Documents:</h4>';
            html += '<ul>';
            
            // CV
            const cvFile = form.cv.files[0];
            html += `<li><strong>CV:</strong> ${cvFile ? cvFile.name : 'Non uploadé'}</li>`;
            
            // Lettre de motivation
            const lettreFile = form.lettre_motivation.files[0];
            html += `<li><strong>Lettre de motivation:</strong> ${lettreFile ? lettreFile.name : 'Non uploadé'}</li>`;
            
            // Portfolio
            const portfolioFile = form.portfolio_fichier ? form.portfolio_fichier.files[0] : null;
            const portfolioLink = form.portfolio_lien ? form.portfolio_lien.value : '';
            if (portfolioFile) {
                html += `<li><strong>Portfolio (fichier):</strong> ${portfolioFile.name}</li>`;
            } else if (portfolioLink) {
                html += `<li><strong>Portfolio (lien):</strong> ${portfolioLink}</li>`;
            } else {
                html += `<li><strong>Portfolio:</strong> Non fourni</li>`;
            }
            
            html += '</ul>';
            
            // Contenu
            html += '<h4>Lettre de motivation:</h4>';
            html += `<div style="white-space: pre-wrap; background: #f8f9fa; padding: 10px; border-radius: 5px;">${form.motivation.value.substring(0, 500)}${form.motivation.value.length > 500 ? '...' : ''}</div>`;
            
            if (form.competences.value) {
                html += '<h4>Compétences:</h4>';
                html += `<div style="white-space: pre-wrap; background: #f8f9fa; padding: 10px; border-radius: 5px;">${form.competences.value.substring(0, 300)}${form.competences.value.length > 300 ? '...' : ''}</div>`;
            }
            
            html += '</div>';
            
            previewContent.innerHTML = html;
            showModal('previewModal');
        }
        
        // Fonctions pour les modals
        function showModal(modalId) {
            document.getElementById(modalId).style.display = 'block';
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        // Copier le lien
        function copyLink() {
            const url = window.location.href;
            navigator.clipboard.writeText(url).then(() => {
                alert('Lien copié dans le presse-papier !');
            });
        }
        
        // Fonctions de partage
        function shareOnWhatsApp() {
            const url = encodeURIComponent(window.location.href);
            const text = encodeURIComponent("Postulez chez SCSM SARL - Formulaire de candidature en ligne");
            window.open(`https://wa.me/?text=${text}%20${url}`, '_blank');
        }
        
        function shareOnLinkedIn() {
            const url = encodeURIComponent(window.location.href);
            window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank');
        }
        
        function shareByEmail() {
            const subject = encodeURIComponent("Formulaire de candidature SCSM SARL");
            const body = encodeURIComponent(`Je vous invite à postuler chez SCSM SARL via ce lien: ${window.location.href}`);
            window.location.href = `mailto:?subject=${subject}&body=${body}`;
        }
        
        function copyShareLink() {
            copyLink();
        }
        
        // Charger les statistiques
        function loadStatistics() {
            // Calculer les jours restants
            const dateLimite = new Date("{{ date_limite.strftime('%Y-%m-%d') }}");
            const aujourdhui = new Date();
            const diffTime = dateLimite - aujourdhui;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            document.getElementById('jours-restants').textContent = diffDays > 0 ? diffDays : 0;
        }
        
        // Compte à rebours
        function initializeCountdown() {
            const countdownElement = document.getElementById('countdown');
            if (!countdownElement) return;
            
            const dateLimite = new Date("{{ date_limite.strftime('%Y-%m-%d') }}");
            
            function updateCountdown() {
                const maintenant = new Date();
                const difference = dateLimite - maintenant;
                
                if (difference <= 0) {
                    countdownElement.textContent = "Terminé";
                    return;
                }
                
                const jours = Math.floor(difference / (1000 * 60 * 60 * 24));
                const heures = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
                
                countdownElement.textContent = `${jours}j ${heures}h ${minutes}m`;
            }
            
            updateCountdown();
            setInterval(updateCountdown, 60000); // Mise à jour chaque minute
        }
        
        // Initialiser le compte à rebours
        initializeCountdown();
        
        // Fermer les modals en cliquant en dehors
        window.addEventListener('click', function(event) {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (event.target == modal) {
                    modal.style.display = 'none';
                }
            });
        });
    </script>
</body>
</html>