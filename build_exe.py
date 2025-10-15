#!/usr/bin/env python3
"""
Script pour créer un exécutable Windows du Wigor Viewer.
Utilise PyInstaller pour packager l'application Tkinter en un seul fichier .exe
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build_dirs():
    """Nettoie les dossiers de build précédents."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Nettoyage du dossier {dir_name}/")
            shutil.rmtree(dir_name, ignore_errors=True)
    
    # Nettoyer les fichiers .spec précédents
    for spec_file in Path('.').glob('*.spec'):
        print(f"🧹 Suppression de {spec_file}")
        spec_file.unlink()

def install_dependencies():
    """Installe PyInstaller si nécessaire."""
    try:
        import PyInstaller
        print("✅ PyInstaller déjà installé")
    except ImportError:
        print("📦 Installation de PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)

def create_executable():
    """Crée l'exécutable avec PyInstaller."""
    print("🔨 Création de l'exécutable Wigor Viewer...")
    
    # Commande PyInstaller avec options optimisées
    cmd = [
        'pyinstaller',
        '--onefile',                    # Un seul fichier exécutable
        '--windowed',                   # Pas de console (pour GUI)
        '--name=WigorViewer',          # Nom de l'exécutable
        '--icon=icon.ico',             # Icône (si elle existe)
        '--add-data=src;src',          # Inclure le dossier src
        '--hidden-import=tkinter',     # Forcer l'inclusion de tkinter
        '--hidden-import=tkinter.ttk', # Forcer l'inclusion de ttk
        '--hidden-import=requests',    # Forcer l'inclusion de requests
        '--hidden-import=bs4',         # Forcer l'inclusion de BeautifulSoup
        '--clean',                     # Nettoyer avant build
        'run.py'                       # Script principal
    ]
    
    # Retirer l'icône si le fichier n'existe pas
    if not os.path.exists('icon.ico'):
        cmd.remove('--icon=icon.ico')
        print("⚠️ Pas d'icône trouvée, exécutable sans icône personnalisée")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Exécutable créé avec succès!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

def create_spec_file():
    """Crée un fichier .spec personnalisé pour plus de contrôle."""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'requests',
        'bs4',
        'datetime',
        'logging',
        're',
        'threading'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WigorViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Pas de console pour l'application GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('WigorViewer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content.strip())
    print("📄 Fichier WigorViewer.spec créé")

def build_from_spec():
    """Construit l'exécutable à partir du fichier .spec."""
    print("🔨 Construction à partir du fichier .spec...")
    try:
        subprocess.run(['pyinstaller', '--clean', 'WigorViewer.spec'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la construction: {e}")
        return False

def create_icon():
    """Crée une icône simple si elle n'existe pas."""
    if not os.path.exists('icon.ico'):
        print("🎨 Création d'une icône simple...")
        # On pourrait créer une icône basique ici, mais pour simplifier on skip
        print("ℹ️ Pas d'icône créée automatiquement. Vous pouvez ajouter icon.ico manuellement.")

def main():
    """Fonction principale de build."""
    print("🚀 Build de l'exécutable Wigor Viewer")
    print("=" * 50)
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists('run.py'):
        print("❌ Erreur: run.py introuvable. Lancez ce script depuis la racine du projet.")
        sys.exit(1)
    
    # Étapes de build
    clean_build_dirs()
    install_dependencies()
    create_icon()
    create_spec_file()
    
    # Tenter la construction
    if build_from_spec():
        print("\\n🎉 BUILD RÉUSSI!")
        print("📁 L'exécutable se trouve dans: dist/WigorViewer.exe")
        print("💡 Vous pouvez distribuer ce fichier sans installer Python")
        
        # Afficher la taille du fichier
        exe_path = Path('dist/WigorViewer.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📊 Taille de l'exécutable: {size_mb:.1f} MB")
    else:
        print("\\n💥 BUILD ÉCHOUÉ!")
        print("🔍 Vérifiez les erreurs ci-dessus et réessayez")
        sys.exit(1)

if __name__ == "__main__":
    main()