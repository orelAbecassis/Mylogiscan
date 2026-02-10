# 📋 Mylogiscan

> **Plateforme de Gestion d'Interventions et de Suivi Client**

Mylogiscan est une application web moderne développée avec Flask, conçue pour faciliter la gestion des plannings d'intervention, le suivi des clients et la communication entre administrateurs et intervenants.

---

## ✨ Fonctionnalités Principales

### 👨‍💼 Espace Administrateur
*   **Tableau de Bord Complet** : Vue d'ensemble des interventions, statistiques, et alertes.
*   **Gestion des Utilisateurs** : Création et modification des comptes Intervenants et Clients.
*   **Planification** : Programmation d'interventions pour n'importe quel client/intervenant.
*   **Validation** : Gestion des demandes de suppression d'intervention (Approbation/Rejet avec motif).
*   **Historique** : Accès complet à l'historique de toutes les missions.

### 👷 Espace Intervenant
*   **Planning Personnel** : Visualisation claire des interventions à venir ("Prochaines Interventions").
*   **Scan QR Code** : Système de validation d'intervention par QR Code (Change le statut en "En cours" / "Terminé").
*   **Gestion des Incidents** : Possibilité de demander la suppression d'une intervention avec un motif justificatif.
*   **Clients Assignés** : Liste des clients avec leurs informations essentielles.

---

## 🛠️ Stack Technique

*   **Backend** : Python, Flask, SQLAlchemy
*   **Frontend** : HTML5, TailwindCSS (CDN), Alpine.js (Interactivité)
*   **Base de Données** : SQLite
*   **Authentification** : Flask-Login

---

## 🚀 Installation et Démarrage

### Pré-requis
*   Python 3.8+
*   pip

### 1. Cloner le projet
```bash
git clone https://github.com/orelAbecassis/Mylogiscan.git
cd Mylogiscan
```

### 2. Créer un environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Mac/Linux
# ou
venv\Scripts\activate     # Sur Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Initialiser la Base de Données
Le projet inclut un script de "seed" pour peupler la base de données avec des données de test.

```bash
python seed.py
```
*Cela créera un administrateur par défaut et quelques intervenants/clients.*

### 5. Démarrer le Serveur
```bash
python run.py
```
Accédez à l'application via : `http://127.0.0.1:5000`

---

## 🔑 Comptes de Démonstration (Seed)

| Rôle | Email / Identifiant | Mot de passe |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin` |
| **Intervenant** | `orel` | `password` |
| **Client** | `yonathan` | `password` |

---

## 📁 Structure du Projet

```
EasyScan/
├── app/
│   ├── __init__.py      # Factory de l'application
│   ├── models.py        # Modèles de base de données (User, Intervention, etc.)
│   ├── routes.py        # Logique des routes et contrôleurs
│   ├── extensions.py    # Extensions Flask (db, login_manager)
│   ├── static/          # Fichiers statiques (CSS, IMGs)
│   └── templates/       # Templates HTML (Jinja2)
├── config.py            # Configuration de l'application
├── run.py               # Point d'entrée
├── seed.py              # Script de peuplement de la BDD
└── requirements.txt     # Dépendances Python
```

---

## 📝 Licence

Ce projet est sous licence MIT.
