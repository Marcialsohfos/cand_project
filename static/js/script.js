// Configuration
const API_URL = '/postuler';
const MAX_FILE_SIZE = {
    cv: 5 * 1024 * 1024, // 5MB
    portfolio_fichier: 10 * 1024 * 1024, // 10MB
    lettre_motivation: 3 * 1024 * 1024 // 3MB
};

class CandidatureApp {
    constructor() {
        this.form = document.getElementById('candidatureForm');
        this.submitBtn = document.getElementById('submitBtn');
        this.previewBtn = document.getElementById('previewBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.progressSection = document.getElementById('progressSection');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.progressPercent = document.getElementById('progressPercent');
        
        this.init();
    }
    
    init() {
        // Événements
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.previewBtn.addEventListener('click', () => this.showPreview());
        this.resetBtn.addEventListener('click', () => this.resetForm());
        
        // Validation en temps réel
        this.setupValidation();
        
        // Compteur de caractères
        this.setupCharacterCounters();
        
        // Tabs portfolio
        this.setupPortfolioTabs();
        
        // Initialiser le drag & drop
        this.setupDragAndDrop();
    }
    
    setupValidation() {
        // Validation email
        const emailInput = document.getElementById('email');
        emailInput.addEventListener('blur', () => this.validateEmail(emailInput.value));
        
        // Validation fichiers
        ['cv', 'portfolio_fichier', 'lettre_motivation'].forEach(field => {
            const input = document.getElementById(field);
            if (input) {
                input.addEventListener('change', (e) => this.validateFile(e.target, field));
            }
        });
    }
    
    setupCharacterCounters() {
        const motivation = document.getElementById('motivation');
        const competences = document.getElementById('competences');
        
        motivation.addEventListener('input', () => {
            document.getElementById('motivation-chars').textContent = motivation.value.length;
        });
        
        competences.addEventListener('input', () => {
            document.getElementById('competences-chars').textContent = competences.value.length;
        });
    }
    
    setupPortfolioTabs() {
        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.getAttribute('data-tab');
                
                // Mettre à jour les tabs
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Afficher le contenu correspondant
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById(`${tabName}-tab`).classList.add('active');
                
                // Mettre à jour les validations
                if (tabName === 'lien') {
                    document.getElementById('portfolio_fichier').removeAttribute('required');
                    document.getElementById('portfolio_lien').setAttribute('required', 'true');
                } else {
                    document.getElementById('portfolio_lien').removeAttribute('required');
                    document.getElementById('portfolio_fichier').setAttribute('required', 'true');
                }
            });
        });
    }
    
    setupDragAndDrop() {
        const zones = document.querySelectorAll('.upload-zone');
        
        zones.forEach(zone => {
            const input = zone.querySelector('input[type="file"]');
            const content = zone.querySelector('.upload-content');
            
            // Drag over
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('dragover');
            });
            
            // Drag leave
            zone.addEventListener('dragleave', () => {
                zone.classList.remove('dragover');
            });
            
            // Drop
            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.classList.remove('dragover');
                
                if (e.dataTransfer.files.length) {
                    input.files = e.dataTransfer.files;
                    this.handleFileSelect(input.files[0], input.id);
                }
            });
            
            // Click
            content.addEventListener('click', () => {
                input.click();
            });
            
            // Change
            input.addEventListener('change', () => {
                if (input.files.length) {
                    this.handleFileSelect(input.files[0], input.id);
                }
            });
        });
    }
    
    async validateEmail(email) {
        const validationDiv = document.getElementById('email-validation');
        
        if (!email) {
            validationDiv.innerHTML = '';
            return false;
        }
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            validationDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Format email invalide';
            validationDiv.className = 'validation-message error';
            return false;
        }
        
        // Vérification supplémentaire (optionnelle)
        validationDiv.innerHTML = '<i class="fas fa-check-circle"></i> Email valide';
        validationDiv.className = 'validation-message success';
        return true;
    }
    
    validateFile(file, fieldName) {
        const maxSize = MAX_FILE_SIZE[fieldName];
        const allowedTypes = {
            cv: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            portfolio_fichier: ['application/pdf', 'image/jpeg', 'image/png'],
            lettre_motivation: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
        };
        
        if (!file) return false;
        
        // Vérifier la taille
        if (file.size > maxSize) {
            this.showMessage(`Le fichier ${file.name} dépasse la taille maximale de ${this.formatBytes(maxSize)}`, 'error');
            document.getElementById(fieldName).value = '';
            return false;
        }
        
        // Vérifier le type
        if (allowedTypes[fieldName] && !allowedTypes[fieldName].includes(file.type)) {
            this.showMessage(`Type de fichier non autorisé pour ${fieldName}`, 'error');
            document.getElementById(fieldName).value = '';
            return false;
        }
        
        return true;
    }
    
    handleFileSelect(file, inputId) {
        const field = inputId.replace('-preview', '');
        const previewDiv = document.getElementById(`${field}-preview`);
        
        if (file && this.validateFile(file, field)) {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                previewDiv.innerHTML = `
                    <div class="file-info">
                        <div class="file-icon">
                            <i class="${this.getFileIcon(file.name)}"></i>
                        </div>
                        <div class="file-details">
                            <h5>${file.name}</h5>
                            <p>${this.formatBytes(file.size)} • ${file.type}</p>
                        </div>
                        <button class="file-remove" onclick="app.removeFile('${field}')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                `;
            };
            
            reader.readAsDataURL(file);
        }
    }
    
    removeFile(field) {
        const input = document.getElementById(field);
        const preview = document.getElementById(`${field}-preview`);
        
        if (input) input.value = '';
        if (preview) preview.innerHTML = '';
    }
    
    async showPreview() {
        if (!this.validateForm()) {
            this.showMessage('Veuillez remplir tous les champs obligatoires', 'error');
            return;
        }
        
        const formData = new FormData(this.form);
        const previewHTML = this.generatePreviewHTML(formData);
        
        document.getElementById('previewContent').innerHTML = previewHTML;
        this.openModal('previewModal');
    }
    
    generatePreviewHTML(formData) {
        return `
            <div class="preview-container">
                <div class="preview-section">
                    <h3><i class="fas fa-user"></i> Informations Personnelles</h3>
                    <div class="preview-grid">
                        <div class="preview-item">
                            <strong>Nom complet:</strong>
                            <span>${formData.get('nom_complet')}</span>
                        </div>
                        <div class="preview-item">
                            <strong>Email:</strong>
                            <span>${formData.get('email')}</span>
                        </div>
                        <div class="preview-item">
                            <strong>Téléphone:</strong>
                            <span>${formData.get('telephone') || 'Non renseigné'}</span>
                        </div>
                        <div class="preview-item">
                            <strong>Ville:</strong>
                            <span>${formData.get('ville')}</span>
                        </div>
                    </div>
                </div>
                
                <div class="preview-section">
                    <h3><i class="fas fa-folder-open"></i> Documents</h3>
                    <div class="documents-preview">
                        <div class="document-item">
                            <i class="fas fa-file-contract"></i>
                            <span>CV: ${document.getElementById('cv').files[0]?.name || 'Non fourni'}</span>
                        </div>
                        <div class="document-item">
                            <i class="fas fa-briefcase"></i>
                            <span>Portfolio: ${formData.get('portfolio_lien') || document.getElementById('portfolio_fichier').files[0]?.name || 'Non fourni'}</span>
                        </div>
                        <div class="document-item">
                            <i class="fas fa-envelope-open-text"></i>
                            <span>Lettre: ${document.getElementById('lettre_motivation').files[0]?.name || 'Non fourni'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="preview-section">
                    <h3><i class="fas fa-comment"></i> Lettre de motivation</h3>
                    <div class="preview-text">
                        ${formData.get('motivation').substring(0, 500)}${formData.get('motivation').length > 500 ? '...' : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        if (!this.validateForm()) {
            this.showMessage('Veuillez vérifier tous les champs obligatoires', 'error');
            return;
        }
        
        if (!document.getElementById('privacy').checked) {
            this.showMessage('Veuillez accepter les conditions de confidentialité', 'error');
            return;
        }
        
        // Désactiver le bouton
        this.submitBtn.disabled = true;
        this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Envoi en cours...';
        
        // Afficher la barre de progression
        this.progressSection.style.display = 'block';
        this.updateProgress(0, 'Préparation de l\'envoi...');
        
        try {
            const formData = new FormData(this.form);
            
            // Simuler la progression
            this.simulateProgress();
            
            // Envoyer la requête
            const response = await fetch(API_URL, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.updateProgress(100, 'Candidature envoyée !');
                this.showSuccess(result);
                this.resetForm();
            } else {
                throw new Error(result.error || 'Erreur lors de la soumission');
            }
            
        } catch (error) {
            this.showMessage(`Erreur: ${error.message}`, 'error');
            this.updateProgress(0, 'Erreur');
        } finally {
            // Réactiver le bouton
            setTimeout(() => {
                this.submitBtn.disabled = false;
                this.submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Soumettre ma candidature';
                this.progressSection.style.display = 'none';
            }, 3000);
        }
    }
    
    validateForm() {
        let isValid = true;
        
        // Champs obligatoires
        const requiredFields = ['nom_complet', 'email', 'ville', 'cv', 'lettre_motivation', 'motivation'];
        
        requiredFields.forEach(field => {
            const element = document.getElementById(field);
            if (element && !element.value.trim()) {
                element.classList.add('error');
                isValid = false;
            } else if (element) {
                element.classList.remove('error');
            }
        });
        
        // Vérifier au moins portfolio lien ou fichier
        const portfolioLien = document.getElementById('portfolio_lien').value;
        const portfolioFichier = document.getElementById('portfolio_fichier').files[0];
        
        if (!portfolioLien && !portfolioFichier) {
            this.showMessage('Veuillez fournir un lien portfolio ou télécharger un fichier', 'error');
            isValid = false;
        }
        
        return isValid;
    }
    
    simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            if (progress >= 90) {
                clearInterval(interval);
                return;
            }
            progress += 10;
            this.updateProgress(progress, `Envoi... ${progress}%`);
        }, 300);
    }
    
    updateProgress(percent, text) {
        this.progressBar.style.width = `${percent}%`;
        this.progressText.textContent = text;
        this.progressPercent.textContent = `${percent}%`;
    }
    
    showSuccess(result) {
        document.getElementById('successMessage').textContent = 
            `Merci ${result.nom} ! Votre candidature a été enregistrée sous la référence CAND${result.id.toString().padStart(6, '0')}.`;
        this.openModal('successModal');
    }
    
    showMessage(message, type) {
        // Créer ou réutiliser un élément de message
        let messageDiv = document.querySelector('.global-message');
        
        if (!messageDiv) {
            messageDiv = document.createElement('div');
            messageDiv.className = 'global-message';
            document.body.appendChild(messageDiv);
        }
        
        messageDiv.innerHTML = `
            <div class="message ${type}">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                ${message}
                <button onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Auto-dismiss après 5 secondes
        setTimeout(() => {
            if (messageDiv.parentElement) {
                messageDiv.remove();
            }
        }, 5000);
    }
    
    resetForm() {
        if (confirm('Voulez-vous vraiment réinitialiser le formulaire ?')) {
            this.form.reset();
            
            // Réinitialiser les prévisualisations
            ['cv', 'portfolio_fichier', 'lettre_motivation'].forEach(field => {
                this.removeFile(field);
            });
            
            // Réinitialiser les compteurs
            document.getElementById('motivation-chars').textContent = '0';
            document.getElementById('competences-chars').textContent = '0';
            
            // Réinitialiser les tabs
            document.querySelectorAll('.tab-btn')[0].click();
            
            this.showMessage('Formulaire réinitialisé', 'success');
        }
    }
    
    openModal(modalId) {
        document.getElementById(modalId).style.display = 'block';
    }
    
    // Utilitaires
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            pdf: 'fas fa-file-pdf text-danger',
            doc: 'fas fa-file-word text-primary',
            docx: 'fas fa-file-word text-primary',
            txt: 'fas fa-file-alt text-secondary',
            jpg: 'fas fa-file-image text-success',
            jpeg: 'fas fa-file-image text-success',
            png: 'fas fa-file-image text-success'
        };
        return icons[ext] || 'fas fa-file text-muted';
    }
}

// Fonctions globales
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function copyLink() {
    const url = window.location.href;
    navigator.clipboard.writeText(url)
        .then(() => alert('Lien copié dans le presse-papier !'))
        .catch(err => console.error('Erreur de copie:', err));
}

function initializeCountdown() {
    const deadline = new Date('2025-12-31T23:59:59').getTime();
    
    function updateCountdown() {
        const now = new Date().getTime();
        const distance = deadline - now;
        
        if (distance < 0) {
            document.getElementById('countdown').textContent = 'Expiré';
            return;
        }
        
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        
        document.getElementById('countdown').textContent = `${days}j ${hours}h ${minutes}m`;
        document.getElementById('jours-restants').textContent = days;
    }
    
    updateCountdown();
    setInterval(updateCountdown, 60000); // Mettre à jour chaque minute
}

async function loadStatistics() {
    try {
        const response = await fetch('/api/candidatures');
        const candidatures = await response.json();
        
        document.getElementById('total-candidatures').textContent = candidatures.length;
    } catch (error) {
        console.error('Erreur chargement statistiques:', error);
    }
}

function shareOnWhatsApp() {
    const text = `Postulez dès maintenant chez SCSM SARL ! Date limite: 31 décembre 2025. ${window.location.href}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
}

function shareOnLinkedIn() {
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent('Formulaire de candidature SCSM SARL');
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank');
}

function shareByEmail() {
    const subject = encodeURIComponent('Formulaire de candidature SCSM SARL');
    const body = encodeURIComponent(`Je vous invite à postuler chez SCSM SARL. Lien: ${window.location.href}\n\nDate limite: 31 décembre 2025`);
    window.open(`mailto:?subject=${subject}&body=${body}`, '_blank');
}

function copyShareLink() {
    copyLink();
}

function printConfirmation() {
    window.print();
}

// Initialiser l'application quand la page est chargée
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new CandidatureApp();
});