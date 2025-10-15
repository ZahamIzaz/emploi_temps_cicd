# Makefile pour automatiser les tâches de développement
.PHONY: help install install-dev test test-unit test-integration lint format type-check security build clean docker run-docker dev coverage

# Variables
PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
ISORT := isort
FLAKE8 := flake8
MYPY := mypy
BANDIT := bandit
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Configuration
PROJECT_NAME := wigor-viewer
DOCKER_IMAGE := $(PROJECT_NAME):latest
VENV_NAME := venv
SRC_DIR := src
TEST_DIR := tests

help: ## Affiche l'aide
	@echo "Commandes disponibles :"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installation des dépendances de production
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev: install ## Installation des dépendances de développement
	$(PIP) install pytest pytest-cov pytest-html pytest-xdist
	$(PIP) install black isort flake8 mypy bandit safety
	$(PIP) install pyinstaller

test: ## Lance tous les tests
	$(PYTEST) $(TEST_DIR)/ -v --tb=short --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing --cov-report=xml

test-unit: ## Lance les tests unitaires uniquement
	$(PYTEST) $(TEST_DIR)/ -v -m "unit" --tb=short

test-integration: ## Lance les tests d'intégration uniquement
	$(PYTEST) $(TEST_DIR)/ -v -m "integration" --tb=short

test-gui: ## Lance les tests GUI
	$(PYTEST) $(TEST_DIR)/ -v -m "gui" --tb=short

test-parallel: ## Lance les tests en parallèle
	$(PYTEST) $(TEST_DIR)/ -v -n auto --tb=short

lint: ## Vérification du style de code (flake8)
	$(FLAKE8) $(SRC_DIR)/ $(TEST_DIR)/ --max-line-length=88 --extend-ignore=E203,W503

format: ## Formatage automatique du code
	$(BLACK) $(SRC_DIR)/ $(TEST_DIR)/
	$(ISORT) $(SRC_DIR)/ $(TEST_DIR)/

format-check: ## Vérification du formatage sans modification
	$(BLACK) --check --diff $(SRC_DIR)/ $(TEST_DIR)/
	$(ISORT) --check-only --diff $(SRC_DIR)/ $(TEST_DIR)/

type-check: ## Vérification des types avec mypy
	$(MYPY) $(SRC_DIR)/ --ignore-missing-imports

security: ## Analyse de sécurité
	$(BANDIT) -r $(SRC_DIR)/ -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true

quality: format-check lint type-check security ## Vérification complète de la qualité du code

coverage: ## Génère un rapport de couverture détaillé
	$(PYTEST) $(TEST_DIR)/ --cov=$(SRC_DIR) --cov-report=html --cov-report=term --cov-report=xml --cov-fail-under=70
	@echo "Rapport de couverture généré dans htmlcov/"

build: ## Construction de l'exécutable avec PyInstaller
	pyinstaller --onefile --windowed --name=WigorViewer \
		--add-data "assets:assets" \
		--hidden-import=tkinter \
		--hidden-import=requests \
		--hidden-import=bs4 \
		run.py

build-dir: ## Construction de l'exécutable en répertoire
	pyinstaller --onedir --windowed --name=WigorViewer \
		--add-data "assets:assets" \
		--hidden-import=tkinter \
		--hidden-import=requests \
		--hidden-import=bs4 \
		run.py

docker-build: ## Construction de l'image Docker
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run: ## Lancement du conteneur Docker
	$(DOCKER) run -it --rm -p 8080:8080 $(DOCKER_IMAGE)

docker-test: ## Tests dans un conteneur Docker
	$(DOCKER_COMPOSE) run --rm wigor-viewer-test

docker-compose-up: ## Lancement avec docker-compose
	$(DOCKER_COMPOSE) up --build

docker-compose-down: ## Arrêt des services docker-compose
	$(DOCKER_COMPOSE) down

clean: ## Nettoyage des fichiers temporaires
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/
	rm -f bandit-report.json safety-report.json coverage.xml pytest-results.xml

dev: install-dev ## Configuration de l'environnement de développement
	@echo "Environnement de développement configuré !"
	@echo "Lancez 'make test' pour vérifier que tout fonctionne"

run: ## Lance l'application
	$(PYTHON) run.py

debug: ## Lance l'application en mode debug
	$(PYTHON) -m pdb run.py

benchmark: ## Lance les tests de performance
	$(PYTEST) $(TEST_DIR)/ --benchmark-only --benchmark-json=benchmark.json

pre-commit: quality test ## Vérifications avant commit
	@echo "✅ Toutes les vérifications sont passées avec succès !"

ci-local: ## Simulation du CI en local
	@echo "🚀 Simulation du pipeline CI/CD en local..."
	make clean
	make install-dev
	make quality
	make test
	make build
	@echo "✅ Pipeline CI/CD simulé avec succès !"

release: ## Préparation d'une release
	@echo "🏗️  Préparation de la release..."
	make clean
	make quality
	make test
	make build
	make docker-build
	@echo "📦 Release prête !"

# Raccourcis utiles
t: test
q: quality
f: format
b: build
c: clean
r: run