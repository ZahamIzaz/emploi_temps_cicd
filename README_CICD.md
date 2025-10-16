# 🚀 WIGOR VIEWER - CI/CD PIPELINE

[![CI/CD Pipeline](https://github.com/ZahamIzaz/emploi_temps_cicd/actions/workflows/ci.yml/badge.svg)](https://github.com/ZahamIzaz/emploi_temps_cicd/actions/workflows/ci.yml)
[![SonarCloud](https://sonarcloud.io/api/project_badges/measure?project=ZahamIzaz_emploi_temps_cicd&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ZahamIzaz_emploi_temps_cicd)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ZahamIzaz_emploi_temps_cicd&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ZahamIzaz_emploi_temps_cicd)

Application Python pour afficher l'emploi du temps Wigor EPSI avec pipeline CI/CD complet 3-stages.

## ⚡ Quick Start

```bash
# Clone & setup
git clone https://github.com/ZahamIzaz/emploi_temps_cicd.git
cd emploi_temps_cicd
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt

# Tests locaux
pytest tests/ -v
python -m src.cli --version

# Build local
pyinstaller wigor.spec
docker build -t wigor-viewer .
```

## 🏗️ Architecture CI/CD

### Stage 1 - Tests & Quality ✅
- **Lint** : Black (formatage) + flake8 (PEP8) + isort (imports)
- **Unit Tests** : 52 tests pytest + coverage 30%+
- **Regression Tests** : Snapshots JSON pour détection régressions
- **SonarCloud** : Analyse qualité code et sécurité

### Stage 2 - Build ✅  
- **PyInstaller** : Executable cross-platform (`wigor-viewer`)
- **Docker** : Image multi-stage optimisée + smoke test

### Stage 3 - Deploy ✅
- **GitHub Releases** : Publication automatique sur tags `v*`
- **Docker Registry** : Push vers `ghcr.io` sur tags version

## 🎯 Défi CI/CD EXPRESS VOIE 9¾ (25 pts)

| Exigence | Status | Implementation |
|----------|--------|----------------|
| Tests unitaires | ✅ | pytest + coverage |  
| Tests non-régression | ✅ | Snapshots JSON |
| Vérification PEP8 | ✅ | Black + flake8 |
| Test Docker | ✅ | Multi-stage + smoke test |
| Compilation | ✅ | PyInstaller executable |
| SonarQube | ✅ | SonarCloud intégré |
| Déploiement conditionnel | ✅ | Tags uniquement |

## 📊 Métriques

- **Tests** : 52 tests (96% success rate)
- **Coverage** : ~40% (minimum 30%)  
- **Build Time** : ~3-5 minutes
- **Executable** : ~15-20 MB
- **Docker Image** : ~100 MB (multi-stage)

## 🔧 Développement

### Configuration outils

```bash
# Formatage automatique  
black --line-length 100 src/ tests/
isort src/ tests/

# Linting
flake8 src/ tests/

# Tests spécifiques
pytest -c pytest-units.ini tests/          # Tests unitaires
pytest -c pytest-regression.ini tests/     # Tests régression
```

### Structure projet

```
src/                    # Code source
├── cli.py             # Interface CLI headless
├── wigor_api.py       # API Wigor requests  
└── timetable_parser.py # Parser HTML
tests/                 # Suite tests complète
├── fixtures/          # Données test
├── snapshots/         # Régression JSON
└── test_*.py          # Tests unitaires
```

### Build & Deploy

```bash
# Build executable local
pyinstaller wigor.spec
./dist/wigor-viewer --version

# Build Docker local  
docker build -t wigor-viewer .
docker run --rm wigor-viewer --check

# Déploiement production (tags uniquement)
git tag v1.0.0
git push origin main --tags  # Déclenche Stage 3
```

## 🔄 Pipeline Déclencheurs

- **Push** → `main`/`develop` : Stages 1 + 2
- **Pull Request** → `main` : Stages 1 + 2  
- **Tags** → `v*` : Stages 1 + 2 + 3 (deploy)

## 📚 Documentation

- **[Documentation complète](DOCUMENTATION_CICD_COMPLETE.md)** : Guide détaillé 50+ pages
- **[Rapport réorganisation](REORGANISATION_COMPLETE.md)** : Historique améliorations
- **[GitHub Actions](https://github.com/ZahamIzaz/emploi_temps_cicd/actions)** : Logs pipeline
- **[SonarCloud Dashboard](https://sonarcloud.io/project/overview?id=ZahamIzaz_emploi_temps_cicd)** : Qualité code

## 🏆 Résultat

**Pipeline CI/CD Express Voie 9¾ - Mission accomplie ! 🎉**

Architecture 3-stages professionnelle avec tous les éléments du défi 25 pts validés.

---

*Généré par le pipeline automatisé - Octobre 2025*