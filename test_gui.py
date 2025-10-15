#!/usr/bin/env python3
"""
Test de lancement de l'interface graphique Wigor Viewer
"""

import sys
import os
import tkinter as tk

# Ajouter le répertoire racine au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🚀 Lancement de Wigor Viewer...")
print(f"📁 Répertoire: {current_dir}")

try:
    # Test d'importation
    from src.gui import WigorViewerGUI
    print("✅ Modules importés avec succès")
    
    # Test de Tkinter
    try:
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre test
        root.destroy()
        print("✅ Tkinter disponible")
    except Exception as e:
        print(f"❌ Erreur Tkinter: {e}")
        sys.exit(1)
    
    # Lancer l'application
    print("🖥️  Lancement de l'interface graphique...")
    app = WigorViewerGUI()
    app.run()
    
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("📦 Vérifiez que tous les modules sont présents")
    sys.exit(1)
except Exception as e:
    print(f"💥 Erreur: {e}")
    sys.exit(1)
finally:
    print("👋 Fermeture de l'application")