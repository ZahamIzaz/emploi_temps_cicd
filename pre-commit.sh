#!/bin/bash

# Script de pré-commit pour Git hooks
# Exécute les vérifications de qualité avant chaque commit

echo "🔍 Vérifications pré-commit en cours..."

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction d'erreur
error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Fonction de succès
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Fonction d'avertissement
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Vérification que nous sommes dans un environnement Python
if ! command -v python &> /dev/null; then
    error "Python n'est pas installé ou accessible"
fi

# Vérification des fichiers Python modifiés
PYTHON_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -z "$PYTHON_FILES" ]; then
    success "Aucun fichier Python modifié"
    exit 0
fi

echo "📄 Fichiers Python modifiés :"
echo "$PYTHON_FILES" | sed 's/^/  - /'

# Installation des dépendances si nécessaire
if ! python -c "import black" 2>/dev/null; then
    warning "Installation des outils de formatage..."
    pip install black isort flake8 mypy bandit
fi

# 1. Formatage avec Black
echo "🎨 Vérification du formatage avec Black..."
if ! python -m black --check --diff $PYTHON_FILES; then
    warning "Le code n'est pas formaté correctement"
    echo "Formatage automatique en cours..."
    python -m black $PYTHON_FILES
    git add $PYTHON_FILES
    success "Code formaté et ajouté au commit"
fi

# 2. Tri des imports avec isort
echo "📦 Vérification des imports avec isort..."
if ! python -m isort --check-only --diff $PYTHON_FILES; then
    warning "Les imports ne sont pas triés correctement"
    echo "Tri automatique en cours..."
    python -m isort $PYTHON_FILES
    git add $PYTHON_FILES
    success "Imports triés et ajoutés au commit"
fi

# 3. Vérification PEP8 avec flake8
echo "📏 Vérification PEP8 avec flake8..."
if ! python -m flake8 $PYTHON_FILES --max-line-length=88 --extend-ignore=E203,W503; then
    error "Le code ne respecte pas les standards PEP8"
fi

# 4. Vérification des types avec mypy (non bloquant)
echo "🔍 Vérification des types avec mypy..."
if ! python -m mypy $PYTHON_FILES --ignore-missing-imports; then
    warning "Problèmes de types détectés (non bloquant)"
else
    success "Vérification des types OK"
fi

# 5. Analyse de sécurité avec bandit (non bloquant)
echo "🔒 Analyse de sécurité avec bandit..."
SOURCE_FILES=$(echo "$PYTHON_FILES" | grep "^src/" || true)
if [ -n "$SOURCE_FILES" ]; then
    if ! python -m bandit $SOURCE_FILES; then
        warning "Problèmes de sécurité détectés (non bloquant)"
    else
        success "Analyse de sécurité OK"
    fi
fi

# 6. Tests rapides sur les fichiers modifiés
echo "🧪 Tests rapides..."
TEST_FILES=$(echo "$PYTHON_FILES" | grep "^tests/" || true)
if [ -n "$TEST_FILES" ] || [ -n "$SOURCE_FILES" ]; then
    if command -v pytest &> /dev/null; then
        if ! python -m pytest --collect-only -q > /dev/null 2>&1; then
            error "Erreurs dans la collection des tests"
        fi
        
        # Exécution des tests unitaires rapides uniquement
        if ! python -m pytest tests/ -x -q --tb=no -m "not slow"; then
            error "Échec des tests rapides"
        fi
        success "Tests rapides OK"
    else
        warning "pytest non disponible, tests ignorés"
    fi
fi

success "Toutes les vérifications pré-commit sont passées !"
echo "🚀 Le commit peut être effectué"