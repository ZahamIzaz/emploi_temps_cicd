#!/usr/bin/env python3
"""
Script de lancement de Wigor Viewer.
Corrige les problèmes d'imports relatifs.
"""

import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer et lancer l'application
if __name__ == "__main__":
    from src.main import main
    main()