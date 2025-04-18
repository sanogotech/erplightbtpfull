
# ERP BTP Light


Voici la **version fusionnée** du cahier des charges minimaliste **ERP BTP Light (Quick Win)** avec l’ajout de la **partie interfacement avec un système de comptabilisation comme JD Edwards**, en bout de chaîne. J’ai intégré cette nouvelle section dans le flux naturel du document (notamment dans les modules, les exports et la partie architecture).

---

## 📘 Cahier des Charges Minimaliste – ERP BTP Light (Quick Win)  
**Objectif** : Remplacer l’utilisation des fichiers Excel et emails désorganisés par une application web légère gérant les **processus clés du BTP**, avec des **workflows par rôle**, **échanges automatisés**, une **interface moderne** et un **interfaçage simplifié avec un ERP comptable externe (ex. JD Edwards)**.

---

### 1. 🎯 Objectifs principaux

- Centraliser les processus BTP dans un outil web unique.
- Gérer plusieurs **flux de travail (workflows)** avec des acteurs différents.
- Faciliter la **collaboration**, la **traçabilité**, et le **suivi** des projets.
- Automatiser des actions simples (relances, alertes, mails).
- Exporter et importer facilement les données (CSV, Excel).
- Préparer une **base évolutive** pour une future industrialisation.
- **Prévoir un module d'interfaçage avec un système comptable de type JD Edwards**.

---

### 2. 🧩 Modules fonctionnels (Quick Win + évolutifs)

| Module | Description | Acteurs impliqués |
|--------|-------------|-------------------|
| **Login / Authentification** | Accès sécurisé avec rôles (JWT ou session) | Tous |
| **Dashboard (Accueil)** | Vue globale personnalisée par rôle | Tous |
| **Clients & Prospection** | Gestion fiches clients, historiques, import CSV | Commercial |
| **Devis & Projets** | Génération devis, gestion statuts, export PDF | Commercial, Direction |
| **Workflow de Validation Devis** | Envoi pour validation, suivi du statut | Commercial, Direction |
| **Planning Travaux** | Tâches par chantier, dates, responsable | Chef Chantier |
| **Suivi & Alertes** | Alertes échéances, mails automatiques | Tous |
| **Facturation** | Génération automatique via devis, export PDF | Comptabilité |
| **Paiements & Recouvrements** | Saisie paiements, relances clients, alertes | Comptabilité |
| **Exports Comptables** | **Génération de fichiers normalisés pour intégration JD Edwards** | Comptabilité, SI |
| **Import Données** | Clients, devis, factures via CSV ou Excel | Admin, Commercial |
| **Emails Automatisés** | Relances factures, validation devis | Tous |
| **Historique et Journalisation** | Suivi des actions par utilisateur | Admin |
| **Interfaçage ERP (JD Edwards)** | **Export de données (factures, paiements, analytique)** via fichiers plats ou API REST/FTP | SI, Comptabilité |

---

### 3. 🔁 Workflows par rôle

| Workflow | Étapes principales | Rôles |
|----------|--------------------|-------|
| **Devis** | Création → Validation → Acceptation client → Facturation | Commercial → Directeur |
| **Projet** | Création → Planification → Suivi → Clôture | Chef Chantier → Directeur |
| **Paiement** | Facture → Paiement partiel/total → Suivi recouvrement | Comptable |
| **Export comptable** | Facture validée → Génération fichier → Transfert vers JD Edwards | Comptable, SI |
| **Alertes** | Déclenchement conditionnel → Notification → Suivi | Automatique / Manuel |

---

### 4. 🧰 Stack technique

| Composant | Technologie |
|----------|-------------|
| **Frontend** | HTML5, CSS3, Bootstrap 5, AngularJS (ou Angular 14+) |
| **Backend** | Python (Flask ou FastAPI) |
| **Base de données** | SQLite (simple et portable) |
| **Authentification** | JWT ou sessions Flask |
| **Envoi email** | SMTP via Flask-Mail ou FastAPI-Mail |
| **Import/Export** | CSV/XLSX avec pandas ou openpyxl |
| **Export comptable** | **Fichiers plats CSV/XML/JSON vers FTP/API REST JD Edwards** |
| **PDF** | wkhtmltopdf ou WeasyPrint (factures, devis) |
| **Notification UI** | Toasts Bootstrap + alertes contextuelles |

---

### 5. 📄 Pages clés à développer

| Page | Fonction |
|------|----------|
| `login.html` | Connexion avec rôle |
| `dashboard.html` | Vue KPI selon rôle |
| `clients.html` | CRUD + import/export CSV |
| `devis.html` | CRUD devis + génération PDF |
| `validation-devis.html` | Validation devis avec workflow |
| `planning.html` | Planification chantiers (tableau ou Kanban) |
| `facturation.html` | Liste factures, génération PDF, paiements |
| `recouvrement.html` | Suivi des paiements, relances |
| `exports-comptables.html` | **Prévisualisation et génération export vers ERP** |
| `journal.html` | Historique des actions |
| `admin.html` | Gestion utilisateurs et rôles |

---

### 6. 📂 Structure du projet

```
erp-btp-light/
│
├── frontend/
│   ├── login.html
│   ├── dashboard.html
│   ├── devis.html
│   ├── planning.html
│   ├── exports-comptables.html
│   └── ...
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── workflows.py
│   ├── exports/
│   │   └── jd_edwards.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── clients.py
│   │   ├── projects.py
│   │   └── exports.py
│
├── db/
│   └── database.sqlite
│
├── static/
│   ├── css/
│   ├── js/
│   └── img/
│
└── templates/
    └── *.html (Jinja2 pour Flask)
```

---

### 7. 💌 Envois automatiques

| Type d’e-mail | Déclencheur | Fréquence |
|---------------|-------------|-----------|
| Relance devis | Devis en attente > 5 jours | Quotidien |
| Relance facture | Facture impayée > 7 jours | Hebdomadaire |
| Notification workflow | Nouvelle tâche / validation en attente | Instantané |
| Rapport hebdo | Résumé de l’activité | Hebdomadaire |
| Échec export ERP | Problème de transfert / format vers JD Edwards | Sur erreur |

---

### 8. 📈 Planning & livrables

| Semaine | Livrables |
|--------|-----------|
| Semaine 1 | Auth + Clients + Devis + Envoi Email |
| Semaine 2 | Workflow validation + Planning + Alertes |
| Semaine 3 | Factures + Paiements + Export CSV |
| Semaine 4 | **Module Export ERP (JD Edwards)** + Design final + Historique + Documentation rapide |

---

### 9. 🔐 Sécurité et bonnes pratiques

- Authentification par rôle
- Nettoyage/validation des entrées
- Contrôle d'accès par routes
- Journalisation des actions sensibles
- Sauvegarde régulière de la base SQLite
- **Sécurisation des exports (formats + transfert SFTP/API avec authentification)**

---

### 🔚 Conclusion

Ce **ERP BTP léger** vise un **résultat rapide et opérationnel**, avec la capacité de :
- **Structurer les processus clés du BTP**,
- **Améliorer la collaboration**,
- Et **s’intégrer facilement dans un système d'information existant**, notamment via l’**export vers un ERP comme JD Edwards**.

---

Souhaitez-vous maintenant :
1. Le **squelette technique Flask (backend + frontend)** prêt à coder ?
2. Un **prototype d’interface cliquable HTML uniquement** ?
3. Ou encore un **exemple d’export structuré (CSV ou JSON) pour JD Edwards** ?

-----------------------------------------------
