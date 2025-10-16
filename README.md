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

---

## 🧪 Lancer les Tests

### Tests Unitaires
```bash
# Tests simples
pytest

# Tests avec couverture
pytest --cov=src --cov-report=html --cov-report=term

# Tests avec rapport XML (pour CI/CD)
pytest --cov=src --cov-report=xml --junitxml=pytest-report.xml
```

### Tests de Non-Régression
```bash
# Tests snapshots
python -m pytest test_regression.py -v

# Mise à jour des snapshots (si changements attendus)
python -m pytest test_regression.py --snapshot-update
```

### Tests avec Tox (Multi-versions Python)
```bash
# Installation tox
pip install tox

# Lancer sur toutes les versions configurées
tox

# Version spécifique
tox -e py310
```

---

## 🔍 Lancer le Linting

### Vérification Complète
```bash
# Formatage (Black)
black --check --diff .

# Import sorting (isort)
isort --check-only --diff .

# Linting PEP8 (Flake8)
flake8 .

# Tout en une fois avec tox
tox -e lint
```

### Auto-Correction
```bash
# Appliquer le formatage
black .
isort .

# Vérification après correction
flake8 .
```

### Analyse Sécurité
```bash
# Scan vulnérabilités code
bandit -r src/

# Scan dépendances
safety check
```

---

## 📦 Générer l'Exécutable

### Build Local
```bash
# Installation PyInstaller
pip install pyinstaller

# Build avec spec file
pyinstaller wigor.spec

# Test de l'exécutable
./dist/wigor --version
./dist/wigor --check
```

### Build Multi-OS (CI/CD)
Le pipeline génère automatiquement des exécutables pour :
- **Windows** : `wigor.exe`
- **Linux** : `wigor`
- **macOS** : `wigor` (Universal Binary)

### Script de Build Automatisé
```bash
# Windows
.\scripts\build_exe.bat

# Linux/macOS
./scripts/build_exe.sh
```

---

## 🐳 Construire/Tester l'Image Docker

### Build Local
```bash
# Construction de l'image
docker build -t wigor-viewer:local .

# Test de l'image
docker run --rm wigor-viewer:local --version
docker run --rm wigor-viewer:local --check

# Mode interactif
docker run -it wigor-viewer:local /bin/bash
```

### Docker Compose (Développement)
```bash
# Démarrage services
docker-compose up -d

# Logs
docker-compose logs -f wigor-viewer

# Arrêt
docker-compose down
```

### Test Automatisé Docker
```bash
# Script de test
./scripts/test_image.sh

# Ou manuellement
docker build -t wigor-test .
docker run --rm wigor-test pytest
```

---

## � SonarCloud - Analyse Qualité

### Configuration

1. **Compte SonarCloud**
   ```bash
   # Créer un compte sur https://sonarcloud.io
   # Importer votre repository GitHub/GitLab
   ```

2. **Configuration Secrets**
   ```bash
   # GitHub : Settings > Secrets > Actions
   SONAR_TOKEN=your_sonar_token_here
   
   # GitLab : Settings > CI/CD > Variables
   SONAR_TOKEN=your_sonar_token_here
   ```

3. **Fichier de Configuration**
   ```properties
   # sonar-project.properties (déjà présent)
   sonar.organization=zahamizaz
   sonar.projectKey=ZahamIzaz_emploi_temps_cicd
   sonar.sources=src/
   sonar.tests=tests/
   ```

### Métriques Analysées
- **🐛 Bugs** : Erreurs potentielles
- **🔐 Vulnérabilités** : Failles sécurité
- **� Code Smells** : Problèmes maintenabilité
- **📊 Couverture** : % code testé
- **🔄 Duplication** : Code dupliqué
- **📏 Complexité** : Complexité cyclomatique

### Accès Rapide
```bash
# URL projet SonarCloud
https://sonarcloud.io/dashboard?id=ZahamIzaz_emploi_temps_cicd
```

---

## 📈 Badge de Couverture

### Configuration Automatique
Les badges sont mis à jour automatiquement via :

1. **GitHub Actions** → Upload coverage vers SonarCloud
2. **SonarCloud** → Génère badges dynamiques
3. **README.md** → Affiche badges temps réel

### Badges Disponibles
```markdown
<!-- Copier dans votre README -->
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ZahamIzaz_emploi_temps_cicd&metric=coverage)](https://sonarcloud.io/dashboard?id=ZahamIzaz_emploi_temps_cicd)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ZahamIzaz_emploi_temps_cicd&metric=alert_status)](https://sonarcloud.io/dashboard?id=ZahamIzaz_emploi_temps_cicd)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=ZahamIzaz_emploi_temps_cicd&metric=bugs)](https://sonarcloud.io/dashboard?id=ZahamIzaz_emploi_temps_cicd)
```

---

## 🚀 Déclenchement du Pipeline

### Déclencheurs Automatiques

#### **GitHub Actions** (`.github/workflows/ci.yml`)
```yaml
on:
  push:
    branches: [ main, develop ]     # Push sur branches principales
    tags: [ 'v*' ]                 # Tags de version (v1.0.0)
  pull_request:
    branches: [ main, develop ]     # Pull requests
```

#### **GitLab CI** (`.gitlab-ci.yml`)
```yaml
rules:
  - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH  # Branch principale
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"  # Merge requests
  - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+.*$/      # Tags semver
```

### Workflow par Événement

| Événement | Jobs Exécutés | Déploiement |
|-----------|---------------|-------------|
| **Push `main`** | Tous (lint, test, sonar, build, docker) | Staging automatique |
| **Push `develop`** | Tous sauf release | Staging automatique |
| **Pull Request** | lint, test, sonar | Aucun |
| **Tag `v*`** | Tous + release | Production (manuel) |
| **Manual Trigger** | Configuration personnalisée | Selon choix |

---

## 🎯 Stratégie "Déploiement Conditionnel"

### Environnements Définis

#### 🧪 **Staging** (Automatique)
```yaml
# Déclenchement
- Branch: main, develop
- Condition: Tests passés
- Action: Deploy automatique

# Environnement
- URL: https://wigor-viewer-staging.example.com
- Base données: staging
- Logs: DEBUG activés
```

#### � **Production** (Manuel)
```yaml
# Déclenchement  
- Tags: v1.0.0, v1.2.3, etc.
- Condition: Validation manuelle requise
- Action: Deploy après approbation

# Environnement
- URL: https://wigor-viewer.example.com  
- Base données: production
- Logs: INFO/ERROR seulement
```

### Gates de Qualité
Avant chaque déploiement :
```yaml
✅ Tests unitaires > 80% succès
✅ Couverture code > 75%
✅ SonarCloud Quality Gate = PASSED
✅ Aucune vulnérabilité CRITICAL
✅ Build exécutables réussi
✅ Tests Docker réussis
```

### Rollback Automatique
```bash
# En cas d'échec déploiement
- Rollback automatique vers version précédente
- Notifications équipe (Slack/Email)
- Logs détaillés disponibles
```

---

## 🏗️ Architecture

### Structure du Projet
```
wigor_viewer/
├── 📁 .github/workflows/     # GitHub Actions CI/CD
│   └── ci.yml               # Pipeline principal
├── 📁 .gitlab/              # GitLab CI/CD  
│   └── .gitlab-ci.yml       # Pipeline GitLab
├── 📁 src/                  # Code source principal
│   ├── __init__.py
│   ├── cli.py              # Interface ligne de commande
│   ├── parser.py           # Parseur emplois du temps
│   ├── gui.py              # Interface graphique
│   └── utils.py            # Utilitaires
├── � tests/               # Tests unitaires
│   ├── test_parser.py      
│   ├── test_gui.py
│   └── test_integration.py
├── 📁 scripts/             # Scripts automation
│   ├── build_exe.sh        # Build exécutables
│   ├── test_image.sh       # Tests Docker
│   └── deploy.sh           # Déploiement
├── 📁 docs/                # Documentation
│   ├── API.md              # Documentation API
│   └── DEPLOYMENT.md       # Guide déploiement
├── 📄 Dockerfile           # Multi-stage Docker
├── 📄 docker-compose.yml   # Orchestration locale
├── � wigor.spec           # Configuration PyInstaller
├── 📄 tox.ini              # Tests multi-versions
├── 📄 sonar-project.properties  # Config SonarCloud
├── 📄 requirements.txt     # Dépendances runtime
├── 📄 requirements-dev.txt # Dépendances développement
├── 📄 pyproject.toml       # Configuration Python moderne
├── 📄 .flake8              # Configuration linting
├── � pytest.ini           # Configuration tests
└── 📄 README.md            # Ce fichier
```

### Fichiers Clés

#### **Configuration CI/CD**
- **`.github/workflows/ci.yml`** : Pipeline GitHub Actions complet
- **`.gitlab-ci.yml`** : Pipeline GitLab CI équivalent  
- **`sonar-project.properties`** : Configuration analyse qualité

#### **Configuration Build**
- **`wigor.spec`** : Spécifications PyInstaller
- **`Dockerfile`** : Image Docker multi-étapes
- **`tox.ini`** : Tests multi-versions Python
- **`pyproject.toml`** : Configuration moderne Python

#### **Tests & Qualité**
- **`test_regression.py`** : Tests non-régression avec snapshots
- **`.flake8`** : Règles linting personnalisées
- **`pytest.ini`** : Configuration framework de tests

#### **Scripts Automation**
- **`scripts/build_exe.sh`** : Build automatisé exécutables
- **`scripts/test_image.sh`** : Tests validation Docker
- **`dev.ps1`** : Script développement Windows

---

## 🔄 Non-Régression & Snapshots

### Principe des Tests Snapshot

Les **tests de non-régression** garantissent que les modifications du code n'introduisent pas de régressions dans le comportement attendu.

#### Fonctionnement
```python
# test_regression.py
def test_parser_output_snapshot():
    """Test que la sortie du parser reste identique"""
    # 1. Parse un fichier EDT de référence
    result = parse_edt_file("test_edt.html")
    
    # 2. Compare avec snapshot enregistré
    assert result == load_snapshot("parser_output.json")
    
    # 3. En cas de différence, affiche diff détaillé
```

### Structure des Snapshots
```
test_snapshots/
├── parser_output_baseline.json      # Sortie parser attendue
├── gui_layout_snapshot.json         # Layout interface  
├── error_handling_cases.json        # Gestion erreurs
└── performance_benchmarks.json      # Métriques performance
```

### Workflow Snapshots

#### **Création Initiale**
```bash
# Première exécution - crée les snapshots de référence
pytest test_regression.py --snapshot-update
```

#### **Tests de Régression**
```bash
# Tests normaux - compare avec snapshots existants
pytest test_regression.py -v

# Sortie en cas de succès
✅ test_parser_output_snapshot PASSED
✅ test_gui_rendering_snapshot PASSED
✅ test_error_handling_snapshot PASSED
```

#### **Détection de Régression**
```bash
# Sortie en cas d'échec  
❌ test_parser_output_snapshot FAILED

# Diff détaillé affiché
SNAPSHOT MISMATCH:
--- Expected (snapshot)
+++ Actual (current)
@@ -15,7 +15,7 @@
   "cours": [
     {
       "matiere": "Mathématiques",
-      "horaire": "08:00-10:00",
+      "horaire": "08:00-09:30",
       "salle": "B101"
     }
```

#### **Mise à Jour Snapshots**
```bash
# Après validation des changements attendus
pytest test_regression.py --snapshot-update

# Commit des nouveaux snapshots
git add test_snapshots/
git commit -m "feat: update snapshots for new parser logic"
```

### Avantages des Tests Snapshot

✅ **Détection Automatique** : Toute régression détectée immédiatement  
✅ **Diff Visuel** : Comparaison claire des changements  
✅ **Maintenance Simple** : Mise à jour facile des références  
✅ **Couverture Complète** : Teste le comportement end-to-end  
✅ **CI/CD Intégré** : Bloque automatiquement les régressions  

### Intégration Pipeline CI/CD

```yaml
# Dans .github/workflows/ci.yml
- name: Run Regression Tests
  run: pytest test_regression.py -v --tb=short
  
# Échec du pipeline si régression détectée
# ✅ Branche bloquée jusqu'à correction
# 📧 Notification équipe automatique
```

---

## 📞 Support & Contribution

### 🐛 Signaler un Bug
1. Vérifier les [issues existantes](https://github.com/username/wigor_viewer/issues)
2. Créer une nouvelle issue avec template
3. Inclure logs et contexte d'exécution

### 🚀 Contribuer
1. Fork le repository
2. Créer une branch feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Add: nouvelle fonctionnalité'`)
4. Push la branch (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

### 📋 Checklist Contribution
- [ ] Tests ajoutés/modifiés
- [ ] Linting passé (`flake8`, `black`, `isort`)
- [ ] Documentation mise à jour
- [ ] Snapshots mis à jour si nécessaire
- [ ] Pipeline CI/CD validé

---

## 📄 License

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👥 Équipe

| Rôle | Nom | Contact |
|------|-----|---------|
| **Product Owner** | [Votre Nom] | [votre.email@example.com] |
| **Tech Lead** | [Nom Tech Lead] | [tech@example.com] |
| **DevOps** | [Nom DevOps] | [devops@example.com] |

---

## 🔗 Liens Utiles

- 📊 **[Dashboard SonarCloud](https://sonarcloud.io/dashboard?id=ZahamIzaz_emploi_temps_cicd)**
- 🚀 **[Pipeline CI/CD](https://github.com/username/wigor_viewer/actions)**
- 🐳 **[Images Docker](https://hub.docker.com/r/username/wigor-viewer)**
- 📚 **[Documentation API](docs/API.md)**
- 🎯 **[Guide Déploiement](docs/DEPLOYMENT.md)**

---

*Généré avec ❤️ par l'équipe WigorViewer - Démonstration DevOps/CI/CD*

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
 
 