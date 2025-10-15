# WigorViewer - Visualisateur d'Emploi du Temps 📅

[![CI/CD Pipeline](https://github.com/username/wigor_viewer/actions/workflows/ci.yml/badge.svg)](https://github.com/username/wigor_viewer/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](https://github.com/username/wigor_viewer/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ZahamIzaz_emploi_temps_cicd&metric=alert_status)](https://sonarcloud.io/dashboard?id=ZahamIzaz_emploi_temps_cicd)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-available-blue)](https://hub.docker.com/r/username/wigor-viewer)

## 📋 Description

**WigorViewer** est une application Python moderne qui permet de visualiser et d'analyser les emplois du temps depuis les systèmes de gestion scolaire. Le projet démontre l'implémentation d'un **pipeline CI/CD complet** avec des pratiques DevOps avancées.

### 🎯 Objectifs du Projet
- ✅ **Tests automatisés** (unitaires + non-régression)
- ✅ **Qualité de code** (linting PEP8, formatage, sécurité)
- ✅ **Build automatisé** (exécutables PyInstaller multi-OS)
- ✅ **Containerisation** (Docker multi-étapes optimisé)
- ✅ **Analyse qualité** (SonarCloud intégré)
- ✅ **Déploiement conditionnel** (branches, tags, environnements)

---

## 🔧 Prérequis

### Système
- **Python 3.8+** (testé sur 3.8, 3.9, 3.10, 3.11, 3.12)
- **Git** pour le versioning
- **Docker** (optionnel, pour la containerisation)

### Comptes Services
- **GitHub/GitLab** (pour le pipeline CI/CD)
- **SonarCloud** (pour l'analyse qualité - optionnel)

---

## � Installation Rapide

### 1. Cloner le Repository
```bash
git clone https://github.com/username/wigor_viewer.git
cd wigor_viewer
```

### 2. Environnement Virtuel
```bash
# Création
python -m venv .venv

# Activation (Windows)
.venv\Scripts\activate

# Activation (Linux/macOS) 
source .venv/bin/activate
```

### 3. Installation des Dépendances
```bash
# Production
pip install -r requirements.txt

# Développement (inclut les outils de test/lint)
pip install -r requirements-dev.txt
```

### 4. Configuration (Optionnel)
```bash
# Copier le fichier de configuration
cp .env.example .env
# Éditer .env avec vos paramètres
```

## 🚀 Utilisation

### Lancement rapide
```bash
# Interface graphique (recommandé)
python run.py

# Ou avec le module principal
python src/main.py --gui
```

### 🆕 Authentification automatique (v2.0)

1. **Récupérer votre URL Wigor :**
   - Se connecter à [wigor.net](https://wigor.net)
   - Naviguer vers votre emploi du temps
   - Copier l'URL complète (contient `wigorservices.net`)

2. **Dans l'application :**
   - 📝 Coller l'URL dans le champ "URL Wigor" 
   - 👤 Saisir votre identifiant EPSI (ex: prenom.nom)
   - 🔒 Saisir votre mot de passe EPSI
   - 🔑 Cliquer "Se connecter avec identifiants"
   - ⏳ Attendre "Connecté ✅"
   - 📋 Cliquer "Charger mon emploi du temps"

### Alternative : Cookies manuels
Si l'authentification automatique échoue :
1. Se connecter à Wigor dans Chrome
2. Copier les cookies (`F12` → Application → Cookies → wigorservices.net)
3. Coller dans le champ "Cookie" de l'application

## 📊 Exemple de sortie

```
🗓️ EMPLOI DU TEMPS - Semaine du 15/01/2024

📅 LUNDI 15/01
  🕘 08:30-10:30 | Développement Web       | Salle A101 | M. DUPONT
  🕙 10:45-12:45 | Base de données        | Salle B205 | Mme MARTIN
  🕐 14:00-16:00 | Projet collaboratif    | Salle C301 | M. BERNARD

📅 MARDI 16/01  
  🕘 09:00-11:00 | Algorithmique          | Salle A203 | M. DURAND
  🕒 13:30-15:30 | Système et réseaux     | Salle B104 | Mme PETIT
  
📅 MERCREDI 17/01
  🕘 08:30-12:30 | Workshop emploi        | Salle C205 | M. ROUSSEAU
  
📊 RÉSUMÉ: 6 cours trouvés cette semaine
```

## 🧪 Tests et validation

### Tests unitaires
```bash
# Tests du parser HTML (14 tests)  
python -m pytest tests/test_parser.py -v

# Avec couverture de code
python -m pytest tests/test_parser.py --cov=src
```

### Tests d'intégration
```bash
# Test complet de l'application
python test_integration.py

# Résultat attendu : 6/6 tests réussis ✅
```

### Tests manuels
```bash
# Mode CLI pour debug
python src/main.py --test

Pour exécuter les tests :
```bash
pytest
```

Pour générer un rapport de couverture :
```bash
pytest --cov=src --cov-report=html
```

## Structure du projet

```
wigor_viewer/
├── src/                    # Code source principal
│   ├── main.py            # Point d'entrée de l'application
│   ├── wigor_api.py       # Interface avec l'API Wigor
│   ├── timetable_parser.py # Parseur des données d'emploi du temps
│   └── gui.py             # Interface graphique
├── tests/                 # Tests unitaires
├── requirements.txt       # Dépendances Python
├── .env.example          # Exemple de configuration
└── pyproject.toml        # Configuration du projet
```

## Licence

MIT License
