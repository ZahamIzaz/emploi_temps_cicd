# Pipeline CI/CD Wigor Viewer

Ce document décrit le pipeline CI/CD complet mis en place pour le projet Wigor Viewer.

## 🚀 Vue d'ensemble

Le pipeline CI/CD est configuré avec GitHub Actions et comprend :
- ✅ Tests automatisés (unitaires, intégration, non-régression)
- 🔍 Analyse de qualité de code (PEP8, sécurité, types)
- 🏗️ Build automatique (PyInstaller + Docker)
- ☁️ Analyse SonarCloud
- 🚢 Déploiement conditionnel (staging/production)

## 📋 Jobs du Pipeline

### 1. **Lint & Quality** (`lint`)
- **Triggers** : Push sur `main`/`develop`, Pull Requests
- **OS** : Ubuntu Latest
- **Actions** :
  - 🎨 Formatage avec Black
  - 📦 Tri des imports avec isort  
  - 📏 Vérification PEP8 avec flake8
  - 🔍 Analyse des types avec mypy
  - 🔒 Sécurité avec bandit & safety

### 2. **Tests & Coverage** (`test`)
- **Triggers** : Push sur `main`/`develop`, Pull Requests
- **Matrix** : 
  - OS : Ubuntu, Windows, macOS
  - Python : 3.8, 3.9, 3.10, 3.11, 3.12
- **Actions** :
  - 🧪 Tests unitaires avec pytest
  - 📊 Couverture de code
  - ☁️ Upload vers Codecov

### 3. **Integration Tests** (`integration-tests`)
- **Triggers** : PR ou push sur `main`
- **Dependencies** : lint, test
- **Actions** :
  - 🔄 Tests d'intégration
  - 🖥️ Tests GUI (headless)

### 4. **SonarCloud** (`sonarcloud`)
- **Triggers** : Push (non-PR du même repo)
- **Dependencies** : test
- **Actions** :
  - 📈 Analyse qualité SonarCloud
  - 🐛 Détection de bugs et code smells

### 5. **Build Executable** (`build-executable`)
- **Matrix** : Ubuntu, Windows, macOS
- **Dependencies** : lint, test
- **Actions** :
  - 📦 Build PyInstaller multi-plateforme
  - ⬆️ Upload des artefacts

### 6. **Build Docker** (`build-docker`)
- **Dependencies** : lint, test
- **Actions** :
  - 🐳 Multi-arch build (amd64, arm64)
  - 📤 Push vers GitHub Container Registry

### 7. **Security Scan** (`security-scan`)
- **Dependencies** : build-docker
- **Actions** :
  - 🛡️ Scan Trivy de l'image Docker
  - 📋 Upload SARIF vers GitHub Security

### 8. **Deploy Staging** (`deploy-staging`)
- **Trigger** : Push sur `develop`
- **Environment** : staging
- **Dependencies** : build-docker, integration-tests

### 9. **Deploy Production** (`deploy-production`)
- **Trigger** : Tags `v*`
- **Environment** : production  
- **Dependencies** : build-docker, security-scan, integration-tests
- **Actions** :
  - 🚀 Déploiement production
  - 📋 Création GitHub Release

## 🌙 Tests Nocturnes

Pipeline séparé (`nightly.yml`) pour :
- 🔄 Tests de régression complets
- 📊 Benchmarks de performance
- 📈 Détection de régressions

## 🛠️ Outils de Développement

### Scripts Locaux
- **Makefile** (Linux/macOS) : `make help`
- **PowerShell** (Windows) : `.\dev.ps1 help`

### Commandes Principales
```bash
# Qualité de code
make quality          # Toutes vérifications
make lint            # PEP8
make format          # Formatage auto
make type-check      # Types
make security        # Sécurité

# Tests
make test            # Tous les tests
make test-unit       # Tests unitaires
make coverage        # Rapport couverture

# Build
make build           # PyInstaller
make docker-build    # Image Docker

# Utilitaires
make clean           # Nettoyage
make ci-local        # Simulation CI locale
```

## 🐳 Docker

### Images Multi-stage
- **Builder** : Compilation et dépendances
- **Production** : Image optimisée runtime

### Docker Compose
- Service principal avec GUI (Xvfb)
- Service de tests
- Monitoring optionnel (Prometheus)

## 🔧 Configuration

### Fichiers de Config
- `pyproject.toml` : Black, isort, coverage, pytest
- `setup.cfg` : Flake8, mypy, coverage legacy
- `sonar-project.properties` : SonarCloud
- `.github/workflows/` : GitHub Actions

### Variables d'Environnement GitHub
```
SONAR_TOKEN          # Token SonarCloud
GITHUB_TOKEN         # Token GitHub (auto)
```

## 🚀 Déploiement

### Environments GitHub
- **staging** : Auto-deploy sur `develop`
- **production** : Auto-deploy sur tags `v*`

### Protection des Branches
- `main` : Reviews requises, status checks
- `develop` : Tests requis

## 📊 Monitoring & Rapports

### Artefacts Générés
- Rapports de tests (JUnit XML, HTML)
- Couverture de code (XML, HTML)
- Rapports de sécurité (JSON)
- Exécutables multi-plateforme
- Images Docker

### Intégrations
- **Codecov** : Couverture de code
- **SonarCloud** : Qualité et sécurité  
- **GitHub Security** : Vulnérabilités
- **GitHub Releases** : Distribution

## 🔄 Workflow de Développement

1. **Feature Branch** → Tests locaux (`make ci-local`)
2. **Pull Request** → Pipeline complet automatique
3. **Merge sur develop** → Deploy staging
4. **Tag release** → Deploy production + GitHub Release

## 📈 Métriques de Qualité

- **Couverture** : > 70% requise
- **PEP8** : Respect strict (flake8)
- **Sécurité** : Scan bandit + safety + Trivy
- **Types** : Vérification mypy
- **Performance** : Benchmarks nocturnes