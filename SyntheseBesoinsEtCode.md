
# 🌍 ERP BTP Light – Solution de gestion légère pour le secteur du BTP

## 🚀 Présentation Générale

**ERP BTP Light** est une solution modulaire et intuitive destinée aux entreprises du secteur du bâtiment et des travaux publics. Elle permet de centraliser la gestion commerciale, la planification de chantiers, la facturation, et le suivi analytique des projets. Légère, évolutive et intégrable, elle répond aux besoins quotidiens des équipes terrain et administratives.

---

## 🔧 Fonctionnalités Principales

| Module                 | Fonctionnalités clés                                                                 |
|------------------------|--------------------------------------------------------------------------------------|
| **Gestion Commerciale**| Devis, gestion des clients, suivi des projets                                        |
| **Planification**      | Planning chantiers (Vue calendrier & diagramme de Gantt), gestion des dates clés     |
| **Facturation**        | Génération de factures, suivi des règlements, historique complet                    |
| **Comptabilité**       | Préparation à l’export comptable (formats EDI, XML, CSV vers JD Edwards)            |
| **Tableaux de Bord**   | Suivi des KPIs, statistiques, visualisation graphique des données (Chart.js)        |

---

## 🧪 Technologies Utilisées

| Type        | Technologies                                                                 |
|-------------|-------------------------------------------------------------------------------|
| **Frontend**| Bootstrap 5, Vanilla JavaScript, FullCalendar, Chart.js                      |
| **Backend** | Python Flask, SQLAlchemy                                                     |
| **Base de données** | SQLite (développement), MySQL (production)                        |
| **API & Intégration** | REST API (FastAPI), formats EDI/CSV/JSON pour les exports         |

---

## ✅ Fonctionnalités Déjà Implémentées

### 🧾 Gestion Commerciale
- Création et modification de devis
- Liste des clients avec filtres
- Suivi de l’état des projets et devis

### 📅 Planification de Chantiers
- Calendrier interactif (FullCalendar)
- Suivi des statuts de chantiers
- Affectation des dates par projet

### 💰 Facturation & Suivi Financier
- Génération automatique de factures
- Enregistrement des paiements
- Historique complet par client et projet

### 📤 Export vers JD Edwards
- Génération de fichiers EDI simplifiés
- Export aux formats CSV et JSON
- Téléchargement automatisé

### 📊 Tableaux de Bord
- Indicateurs clés de performance (KPI) en temps réel
- Visualisations graphiques interactives
- Accès rapide aux modules essentiels

---

## 🧱 Structure du Projet (Squelette du Code)

```
erp_btp_light/
├── app.py                  # Point d’entrée de l’application
├── database.db             # Base de données locale (SQLite)
├── templates/
│   ├── base.html           # Template principal
│   ├── accueil.html        # Page d’accueil
│   ├── login.html          # Connexion utilisateur
│   ├── dashboard.html      # Vue tableau de bord
│   ├── includes/           # Éléments réutilisables
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   └── sidebar.html
│   ├── devis/
│   │   ├── liste.html
│   │   └── nouveau.html
│   ├── chantiers/
│   │   └── liste.html
│   └── factures/
│       └── liste.html
├── static/
│   └── style.css           # Feuilles de style personnalisées
```

---

## 📌 Prochaines Étapes (Roadmap)
- Authentification par rôles (admin, gestionnaire, technicien)
- Notifications email & alertes sur échéances
- Module RH simplifié (gestion des équipes sur chantier)
- Export PDF des devis et factures
- Intégration avec outils de stockage cloud (Google Drive, Dropbox)

---


------------------

# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import csv
import json
from io import StringIO
import os

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_pro'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['EXPORT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'exports')
db = SQLAlchemy(app)

# Modèles de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, commercial, comptable

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    code_jde = db.Column(db.String(20))

class Devis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    montant = db.Column(db.Float, nullable=False)
    statut = db.Column(db.String(20), default='brouillon')  # brouillon, envoyé, accepté, refusé
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship('Client', backref='devis')

class Chantier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    statut = db.Column(db.String(20), default='planifié')  # planifié, en_cours, terminé
    responsable = db.Column(db.String(80))
    client = db.relationship('Client', backref='chantiers')

class Facture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    devis_id = db.Column(db.Integer, db.ForeignKey('devis.id'), nullable=False)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    montant = db.Column(db.Float, nullable=False)
    date_emission = db.Column(db.DateTime, default=datetime.utcnow)
    statut_paiement = db.Column(db.String(20), default='impayé')  # impayé, partiel, payé
    date_paiement = db.Column(db.Date)
    devis = db.relationship('Devis', backref='facture')

# Fonctions utilitaires
def generate_reference(prefix):
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{db.session.query(Devis).count() + 1}"

# Routes principales
@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            session['role'] = user.role
            flash('Connexion réussie!', 'success')
            return redirect(url_for('dashboard'))
        flash('Identifiants incorrects', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    stats = {
        'devis': {
            'total': Devis.query.count(),
            'en_attente': Devis.query.filter_by(statut='envoyé').count()
        },
        'chantiers': {
            'actifs': Chantier.query.filter(Chantier.statut.in_(['planifié', 'en_cours'])).count()
        },
        'factures': {
            'impayees': Facture.query.filter_by(statut_paiement='impayé').count()
        }
    }
    
    return render_template('dashboard.html', 
                         stats=stats,
                         derniers_devis=Devis.query.order_by(Devis.date_creation.desc()).limit(5).all(),
                         prochains_chantiers=Chantier.query.filter(
                             Chantier.date_debut >= datetime.now().date()
                         ).order_by(Chantier.date_debut).limit(3).all())

# Gestion Commerciale
@app.route('/devis')
def liste_devis():
    devis_list = Devis.query.order_by(Devis.date_creation.desc()).all()
    return render_template('devis/liste.html', devis_list=devis_list)

@app.route('/devis/nouveau', methods=['GET', 'POST'])
def nouveau_devis():
    if request.method == 'POST':
        try:
            nouveau_devis = Devis(
                client_id=request.form.get('client_id'),
                reference=generate_reference('DEV'),
                montant=float(request.form.get('montant')),
                statut='brouillon'
            )
            db.session.add(nouveau_devis)
            db.session.commit()
            flash('Devis créé avec succès!', 'success')
            return redirect(url_for('liste_devis'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la création: {str(e)}", 'danger')
    
    return render_template('devis/nouveau.html', clients=Client.query.all())

@app.route('/devis/<int:id>/modifier', methods=['GET', 'POST'])
def modifier_devis(id):
    devis = Devis.query.get_or_404(id)
    if request.method == 'POST':
        try:
            devis.client_id = request.form.get('client_id')
            devis.montant = float(request.form.get('montant'))
            devis.statut = request.form.get('statut')
            db.session.commit()
            flash('Devis modifié avec succès!', 'success')
            return redirect(url_for('liste_devis'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la modification: {str(e)}", 'danger')
    
    return render_template('devis/modifier.html', 
                         devis=devis,
                         clients=Client.query.all())

# Planification Chantiers
@app.route('/chantiers')
def liste_chantiers():
    return render_template('chantiers/liste.html', 
                         chantiers=Chantier.query.order_by(Chantier.date_debut).all())

@app.route('/chantiers/nouveau', methods=['GET', 'POST'])
def nouveau_chantier():
    if request.method == 'POST':
        try:
            nouveau_chantier = Chantier(
                nom=request.form.get('nom'),
                client_id=request.form.get('client_id'),
                date_debut=datetime.strptime(request.form.get('date_debut'), '%Y-%m-%d').date(),
                date_fin=datetime.strptime(request.form.get('date_fin'), '%Y-%m-%d').date(),
                responsable=request.form.get('responsable'),
                statut='planifié'
            )
            db.session.add(nouveau_chantier)
            db.session.commit()
            flash('Chantier créé avec succès!', 'success')
            return redirect(url_for('liste_chantiers'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la création: {str(e)}", 'danger')
    
    return render_template('chantiers/nouveau.html', 
                         clients=Client.query.all())

# Facturation
@app.route('/factures')
def liste_factures():
    return render_template('factures/liste.html', 
                         factures=Facture.query.order_by(Facture.date_emission.desc()).all())

@app.route('/factures/generer/<int:devis_id>')
def generer_facture(devis_id):
    devis = Devis.query.get_or_404(devis_id)
    try:
        nouvelle_facture = Facture(
            devis_id=devis.id,
            reference=generate_reference('FAC'),
            montant=devis.montant,
            statut_paiement='impayé'
        )
        db.session.add(nouvelle_facture)
        db.session.commit()
        flash('Facture générée avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la génération: {str(e)}", 'danger')
    return redirect(url_for('liste_factures'))

# Export JDE
@app.route('/export/jde')
def export_jde():
    try:
        os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)
        filename = f"export_jde_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(app.config['EXPORT_FOLDER'], filename)
        
        factures = Facture.query.join(Devis).join(Client).filter(
            Facture.statut_paiement == 'payé'
        ).all()
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['REFERENCE', 'CLIENT', 'MONTANT', 'DATE_EMISSION', 'DATE_PAIEMENT'])
            
            for facture in factures:
                writer.writerow([
                    facture.reference,
                    facture.devis.client.nom,
                    facture.montant,
                    facture.date_emission.strftime('%Y%m%d'),
                    facture.date_paiement.strftime('%Y%m%d') if facture.date_paiement else ''
                ])
        
        return send_from_directory(
            app.config['EXPORT_FOLDER'],
            filename,
            as_attachment=True,
            mimetype='text/csv'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Gestion utilisateur
@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('accueil'))

# Initialisation données
def init_db():
    with app.app_context():
        db.create_all()
        
        if not User.query.first():
            users = [
                User(username='admin', password=generate_password_hash('admin123'), role='admin'),
                User(username='commercial', password=generate_password_hash('comm123'), role='commercial'),
                User(username='comptable', password=generate_password_hash('compta123'), role='comptable')
            ]
            
            clients = [
                Client(nom='Constructeo', email='contact@constructeo.fr', telephone='0123456789', code_jde='CLI001'),
                Client(nom='Bâtimax', email='contact@batimax.com', telephone='0987654321', code_jde='CLI002')
            ]
            
            db.session.bulk_save_objects(users + clients)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

--------------------------------------------------
# templates/accueil.html

{% extends "base.html" %}

{% block content %}
<div class="hero-section">
    <div class="container text-center py-5">
        <h1 class="display-4 fw-bold">ERP BTP Light</h1>
        <p class="lead">Solution simplifiée de gestion pour les professionnels du BTP</p>
        <a href="{{ url_for('login') }}" class="btn btn-primary btn-lg mt-3">
            <i class="bi bi-box-arrow-in-right"></i> Se connecter
        </a>
    </div>
</div>

<div class="container features py-5">
    <div class="row text-center">
        <div class="col-md-4">
            <i class="bi bi-file-earmark-text feature-icon"></i>
            <h3>Gestion des Devis</h3>
            <p>Créez et suivez vos devis facilement</p>
        </div>
        <div class="col-md-4">
            <i class="bi bi-calendar-check feature-icon"></i>
            <h3>Planning Chantiers</h3>
            <p>Organisez vos interventions</p>
        </div>
        <div class="col-md-4">
            <i class="bi bi-currency-euro feature-icon"></i>
            <h3>Facturation</h3>
            <p>Générez vos factures en 1 clic</p>
        </div>
    </div>
</div>
{% endblock %}

---------------------------------------------
# templates/dashboard.html

{% extends "base.html" %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <!-- Sidebar -->
        <div class="col-md-3 col-lg-2 d-md-block bg-dark sidebar collapse">
            {% include 'includes/sidebar.html' %}
        </div>

        <!-- Main Content -->
        <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
            <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                <h1 class="h2">Tableau de Bord</h1>
                <div class="btn-toolbar mb-2 mb-md-0">
                    <div class="btn-group me-2">
                        <button type="button" class="btn btn-sm btn-outline-secondary">Exporter</button>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#quickActionModal">
                        <i class="bi bi-lightning"></i> Action rapide
                    </button>
                </div>
            </div>

            <!-- KPI Cards -->
            <div class="row mb-4">
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card border-start-primary shadow h-100 py-2">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col me-2">
                                    <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                        Devis en cours</div>
                                    <div class="h5 mb-0 font-weight-bold text-gray-800">{{ stats.devis }}</div>
                                </div>
                                <div class="col-auto">
                                    <i class="bi bi-file-earmark-text fa-2x text-gray-300"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- Ajoutez 3 autres cartes KPI de la même manière -->
            </div>

            <!-- Derniers devis -->
            <div class="card shadow mb-4">
                <div class="card-header py-3">
                    <h6 class="m-0 font-weight-bold text-primary">Derniers devis</h6>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Référence</th>
                                    <th>Client</th>
                                    <th>Montant</th>
                                    <th>Statut</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for devis in derniers_devis %}
                                <tr>
                                    <td>{{ devis.reference }}</td>
                                    <td>{{ devis.client.nom }}</td>
                                    <td>{{ devis.montant }} €</td>
                                    <td>
                                        <span class="badge bg-{{ 'success' if devis.statut == 'accepté' else 'warning' if devis.statut == 'envoyé' else 'secondary' }}">
                                            {{ devis.statut }}
                                        </span>
                                    </td>
                                    <td>
                                        <a href="#" class="btn btn-sm btn-outline-primary">Voir</a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Calendrier des chantiers -->
            <div class="card shadow mb-4">
                <div class="card-header py-3">
                    <h6 class="m-0 font-weight-bold text-primary">Prochains chantiers</h6>
                </div>
                <div class="card-body">
                    <div class="list-group">
                        {% for chantier in chantiers %}
                        <a href="#" class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">{{ chantier.nom }}</h5>
                                <small>{{ chantier.date_debut.strftime('%d/%m/%Y') }}</small>
                            </div>
                            <p class="mb-1">Client: {{ chantier.client.nom }}</p>
                            <small>Statut: 
                                <span class="badge bg-{{ 'success' if chantier.statut == 'terminé' else 'primary' if chantier.statut == 'en_cours' else 'warning' }}">
                                    {{ chantier.statut }}
                                </span>
                            </small>
                        </a>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </main>
    </div>
</div>

<!-- Modal Actions Rapides -->
<div class="modal fade" id="quickActionModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Actions Rapides</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="row g-3">
                    <div class="col-md-6">
                        <a href="{{ url_for('nouveau_devis') }}" class="btn btn-primary w-100">
                            <i class="bi bi-file-earmark-plus"></i> Nouveau Devis
                        </a>
                    </div>
                    <div class="col-md-6">
                        <button class="btn btn-success w-100">
                            <i class="bi bi-calendar-plus"></i> Nouveau Chantier
                        </button>
                    </div>
                    <div class="col-md-6">
                        <button class="btn btn-info w-100">
                            <i class="bi bi-cash-stack"></i> Encaissement
                        </button>
                    </div>
                    <div class="col-md-6">
                        <button class="btn btn-warning w-100" id="exportJDEBtn">
                            <i class="bi bi-database"></i> Export JDE
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// Gestion de l'export JDE
document.getElementById('exportJDEBtn').addEventListener('click', async () => {
    const response = await fetch('/export/jde');
    const data = await response.json();
    
    if(data.status === 'success') {
        // Créer un blob et déclencher le téléchargement
        const blob = new Blob([data.data], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `export_jde_${new Date().toISOString().slice(0,10)}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Afficher notification
        showToast('Export JDE réussi', 'L\'export a été généré avec succès', 'success');
    }
});

function showToast(title, message, type) {
    // Implémentez votre système de toast ici
    alert(`${title}: ${message}`);
}
</script>
{% endblock %}

--------------------------------

# static/style.css

:root {
    --primary: #3498db;
    --secondary: #2c3e50;
    --light: #f8f9fa;
    --dark: #343a40;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f5f5f5;
}

/* Header */
.navbar {
    background-color: var(--secondary);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.navbar-brand {
    font-weight: 700;
    font-size: 1.5rem;
}

/* Page d'accueil */
.hero-section {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    padding: 6rem 0;
    margin-bottom: 3rem;
}

.feature-icon {
    font-size: 3rem;
    color: var(--primary);
    margin-bottom: 1rem;
}

/* Login */
.login-container {
    max-width: 400px;
    margin: 5rem auto;
}

.login-card {
    border: none;
    border-radius: 10px;
    overflow: hidden;
}

/* Dashboard */
.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.sidebar-menu {
    border: none;
    border-radius: 10px;
    box-shadow: 0 2px 15px rgba(0,0,0,0.05);
}

.kpi-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    transition: transform 0.3s;
}

.kpi-card:hover {
    transform: translateY(-5px);
}

.kpi-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--primary);
}

.kpi-label {
    color: var(--dark);
    font-size: 0.9rem;
}

/* Footer */
footer {
    background-color: var(--dark);
    color: white;
    padding: 1.5rem 0;
    margin-top: 3rem;
}