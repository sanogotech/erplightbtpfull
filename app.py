from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import csv
import os
import functools

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_pro'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['EXPORT_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'exports')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

db = SQLAlchemy(app)

# ========================== Sécurité =============================

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Veuillez vous connecter', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                flash('Accès non autorisé', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ======================== Modèles ================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

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
    statut = db.Column(db.String(20), default='brouillon')
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship('Client', backref='devis')

class Chantier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    statut = db.Column(db.String(20), default='planifié')
    responsable = db.Column(db.String(80))
    client = db.relationship('Client', backref='chantiers')

class Facture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    devis_id = db.Column(db.Integer, db.ForeignKey('devis.id'), nullable=False)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    montant = db.Column(db.Float, nullable=False)
    date_emission = db.Column(db.DateTime, default=datetime.utcnow)
    statut_paiement = db.Column(db.String(20), default='impayé')
    date_paiement = db.Column(db.Date)
    devis = db.relationship('Devis', backref='facture')

# ====================== Fonctions utilitaires ======================

def generate_reference(prefix):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = os.urandom(2).hex()
    count = Devis.query.count() if prefix == 'DEV' else Facture.query.count()
    return f"{prefix}-{timestamp}-{count + 1:04d}-{random_suffix}"

# ======================== Gestion erreurs ===========================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.before_request
def before_request():
    session.permanent = True
    if 'user' in session:
        session.modified = True

# ======================== Authentification ==========================

@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            session['role'] = user.role
            session.permanent = True
            flash('Connexion réussie !', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Vous avez été déconnecté avec succès!', 'info')
    return redirect(url_for('accueil'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        stats = {
            'devis': {'total': Devis.query.count(), 'envoyes': Devis.query.filter_by(statut='envoyé').count()},
            'chantiers': {'actifs': Chantier.query.filter(Chantier.statut.in_(['planifié', 'en_cours'])).count()},
            'factures': {'impayees': Facture.query.filter_by(statut_paiement='impayé').count()}
        }
        return render_template('dashboard.html', 
                               stats=stats,
                               derniers_devis=Devis.query.order_by(Devis.date_creation.desc()).limit(5).all(),
                               prochains_chantiers=Chantier.query.filter(
                                   Chantier.date_debut >= datetime.now().date()
                               ).order_by(Chantier.date_debut).limit(3).all())
    except Exception as e:
        flash(f"Erreur tableau de bord: {str(e)}", 'danger')
        return redirect(url_for('accueil'))

# ======================== Devis ===========================

@app.route('/devis')
def liste_devis():
    return render_template('devis/liste.html', devis_list=Devis.query.order_by(Devis.date_creation.desc()).all())

@app.route('/devis/nouveau', methods=['GET', 'POST'])
def nouveau_devis():
    if request.method == 'POST':
        try:
            devis = Devis(
                client_id=request.form.get('client_id'),
                reference=generate_reference('DEV'),
                montant=float(request.form.get('montant')),
                statut='brouillon'
            )
            db.session.add(devis)
            db.session.commit()
            flash('Devis créé!', 'success')
            return redirect(url_for('liste_devis'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur: {str(e)}", 'danger')
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
            flash('Devis modifié!', 'success')
            return redirect(url_for('liste_devis'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur: {str(e)}", 'danger')
    return render_template('devis/modifier.html', devis=devis, clients=Client.query.all())

# ======================== Chantiers ===========================

@app.route('/chantiers')
def liste_chantiers():
    return render_template('chantiers/liste.html', chantiers=Chantier.query.order_by(Chantier.date_debut).all())

@app.route('/chantiers/nouveau', methods=['GET', 'POST'])
def nouveau_chantier():
    if request.method == 'POST':
        try:
            chantier = Chantier(
                nom=request.form.get('nom'),
                client_id=request.form.get('client_id'),
                date_debut=datetime.strptime(request.form.get('date_debut'), '%Y-%m-%d').date(),
                date_fin=datetime.strptime(request.form.get('date_fin'), '%Y-%m-%d').date(),
                responsable=request.form.get('responsable'),
                statut='planifié'
            )
            db.session.add(chantier)
            db.session.commit()
            flash('Chantier créé!', 'success')
            return redirect(url_for('liste_chantiers'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur: {str(e)}", 'danger')
    return render_template('chantiers/nouveau.html', clients=Client.query.all())

# ======================== Facturation ===========================

@app.route('/factures')
def liste_factures():
    return render_template('factures/liste.html', factures=Facture.query.order_by(Facture.date_emission.desc()).all())

@app.route('/factures/generer/<int:devis_id>')
def generer_facture(devis_id):
    devis = Devis.query.get_or_404(devis_id)
    try:
        facture = Facture(
            devis_id=devis.id,
            reference=generate_reference('FAC'),
            montant=devis.montant,
            statut_paiement='impayé'
        )
        db.session.add(facture)
        db.session.commit()
        flash('Facture générée!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur: {str(e)}", 'danger')
    return redirect(url_for('liste_factures'))

# ======================== Export JDE ===========================

@app.route('/export/jde')
@login_required
@role_required(['admin', 'comptable'])
def export_jde():
    try:
        os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)
        filename = f"export_jde_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(app.config['EXPORT_FOLDER'], filename)

        factures = Facture.query.join(Devis).join(Client).filter(
            Facture.statut_paiement == 'payé'
        ).all()

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Code JDE', 'Nom Client', 'Montant', 'Date Paiement', 'Référence Facture'])
            for facture in factures:
                writer.writerow([
                    facture.devis.client.code_jde or '',
                    facture.devis.client.nom,
                    facture.montant,
                    facture.date_paiement.strftime('%Y-%m-%d') if facture.date_paiement else '',
                    facture.reference
                ])

        return send_from_directory(app.config['EXPORT_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        flash(f"Erreur export JDE: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

# ======================== Lancement ===========================

def init_demo_data():
    try:
        # Create users
        users = [
            User(username='admin', password=generate_password_hash('admin123'), role='admin'),
            User(username='commercial', password=generate_password_hash('comm123'), role='commercial'),
            User(username='comptable', password=generate_password_hash('compta123'), role='comptable')
        ]
        db.session.bulk_save_objects(users)
        db.session.commit()

        # Create clients
        clients = [
            Client(nom='Constructeo', email='contact@constructeo.fr', telephone='0123456789', code_jde='CLI001', adresse='15 rue de la Construction'),
            Client(nom='Bâtimax', email='contact@batimax.com', telephone='0987654321', code_jde='CLI002', adresse='42 avenue du Bâtiment'),
            Client(nom='RenovPro', email='contact@renovpro.fr', telephone='0567891234', code_jde='CLI003', adresse='8 boulevard de la Rénovation')
        ]
        db.session.bulk_save_objects(clients)
        db.session.commit()

        # Create some devis
        devis = [
            Devis(client_id=1, reference='DEV-20240101-001', montant=15000.0, statut='accepté', date_creation=datetime(2024, 1, 1)),
            Devis(client_id=2, reference='DEV-20240102-002', montant=8500.0, statut='envoyé', date_creation=datetime(2024, 1, 2)),
            Devis(client_id=3, reference='DEV-20240103-003', montant=12000.0, statut='brouillon', date_creation=datetime(2024, 1, 3))
        ]
        db.session.bulk_save_objects(devis)
        db.session.commit()

        # Create some chantiers
        chantiers = [
            Chantier(nom='Rénovation façade', client_id=1, date_debut=date(2024, 2, 1), date_fin=date(2024, 3, 15),
                    statut='en_cours', responsable='Pierre Martin'),
            Chantier(nom='Installation électrique', client_id=2, date_debut=date(2024, 3, 1), date_fin=date(2024, 3, 30),
                    statut='planifié', responsable='Jean Dupont'),
            Chantier(nom='Isolation combles', client_id=3, date_debut=date(2024, 1, 15), date_fin=date(2024, 2, 15),
                    statut='terminé', responsable='Sophie Durant')
        ]
        db.session.bulk_save_objects(chantiers)
        db.session.commit()

        # Create some factures
        factures = [
            Facture(devis_id=1, reference='FAC-20240115-001', montant=15000.0, statut_paiement='payé',
                   date_emission=datetime(2024, 1, 15), date_paiement=date(2024, 1, 30)),
            Facture(devis_id=2, reference='FAC-20240116-002', montant=8500.0, statut_paiement='impayé',
                   date_emission=datetime(2024, 1, 16))
        ]
        db.session.bulk_save_objects(factures)
        db.session.commit()

        print("Demo data initialized successfully!")
        return True

    except Exception as e:
        print(f"Error initializing demo data: {e}")
        db.session.rollback()
        return False

if __name__ == '__main__':
    with app.app_context():
        # Recreate all tables
        db.drop_all()
        db.create_all()
        
        # Initialize demo data
        if init_demo_data():
            print("Database ready with demo data!")
        else:
            print("Error occurred during initialization!")
    
    # Run the application
    app.run(debug=True)
