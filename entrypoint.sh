#!/bin/bash

# Script d'entrée pour l'image Docker
# Gestion des signaux et configuration de l'environnement

set -e

# Configuration des variables d'environnement
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Fonction de nettoyage
cleanup() {
    echo "Arrêt gracieux du conteneur..."
    # Arrêt de Xvfb si démarré
    if [ -n "$XVFB_PID" ]; then
        kill $XVFB_PID 2>/dev/null || true
    fi
    exit 0
}

# Gestion des signaux
trap cleanup SIGTERM SIGINT

# Vérification de la santé de l'application
health_check() {
    python -c "
from src.wigor_api import WigorAPI
print('✅ Application healthy')
" || {
    echo "❌ Health check failed"
    exit 1
}
}

# Démarrage de Xvfb pour les tests GUI
start_xvfb() {
    echo "🖥️  Démarrage du serveur d'affichage virtuel..."
    Xvfb :99 -screen 0 1024x768x24 &
    XVFB_PID=$!
    export DISPLAY=:99
    
    # Attendre que Xvfb soit prêt
    sleep 2
    echo "✅ Serveur d'affichage prêt"
}

# Mode de démarrage
case "${1:-run}" in
    "test")
        echo "🧪 Mode test"
        start_xvfb
        health_check
        exec pytest tests/ -v --tb=short
        ;;
    "health")
        echo "🏥 Vérification de santé"
        health_check
        ;;
    "shell")
        echo "🐚 Mode shell interactif"
        exec /bin/bash
        ;;
    "run"|*)
        echo "🚀 Démarrage de l'application"
        start_xvfb
        health_check
        exec python run.py "$@"
        ;;
esac