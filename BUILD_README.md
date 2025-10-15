# 📦 Guide de création d'exécutable - Wigor Viewer

Ce guide vous explique comment créer un exécutable Windows (.exe) autonome pour l'application Wigor Viewer.

## 🚀 Méthodes de build

### Méthode 1 : Script automatique (Recommandé)

**Via le fichier batch :**
```bash
# Double-cliquez sur build.bat
# OU depuis l'invite de commande :
build.bat
```

**Via Python :**
```bash
python build_exe.py
```

### Méthode 2 : PyInstaller manuel

```bash
# Installation de PyInstaller (si pas déjà fait)
pip install pyinstaller

# Création de l'exécutable
pyinstaller --onefile --windowed --name=WigorViewer --add-data="src;src" run.py
```

## 📋 Prérequis

- **Python 3.7+** installé
- **Modules requis** : Installés via `pip install -r requirements.txt`
- **Windows** (pour créer un .exe Windows)

## 📁 Structure après build

```
wigor_viewer/
├── build/                  # Dossier temporaire (peut être supprimé)
├── dist/
│   └── WigorViewer.exe    # 🎯 VOTRE EXÉCUTABLE ICI
├── WigorViewer.spec       # Configuration PyInstaller
├── build_exe.py          # Script de build
└── build.bat             # Script batch Windows
```

## ✅ Test de l'exécutable

1. Naviguez vers le dossier `dist/`
2. Double-cliquez sur `WigorViewer.exe`
3. L'application devrait se lancer sans installer Python

## 📦 Distribution

L'exécutable `WigorViewer.exe` est **autonome** :
- ✅ Pas besoin d'installer Python sur le PC cible
- ✅ Toutes les dépendances sont incluses
- ✅ Fonctionne sur Windows 7, 8, 10, 11
- 📊 Taille typique : ~15-30 MB

## 🔧 Options avancées

### Personnalisation de l'icône
1. Ajoutez un fichier `icon.ico` à la racine
2. Relancez le build - l'icône sera automatiquement incluse

### Optimisation de la taille
- L'option `--onefile` crée un seul fichier mais plus gros
- Pour un exécutable plus petit, supprimez `--onefile` (crée un dossier avec plusieurs fichiers)

### Debug
Si l'exécutable ne fonctionne pas :
1. Supprimez `--windowed` pour voir les erreurs dans la console
2. Testez d'abord avec `python run.py`
3. Vérifiez les logs dans `build/WigorViewer/`

## 🐛 Résolution de problèmes

### "Python non trouvé"
- Installez Python depuis https://python.org
- Cochez "Add Python to PATH" lors de l'installation

### "Module non trouvé"
```bash
pip install -r requirements.txt
```

### "Erreur lors du build"
1. Supprimez les dossiers `build/` et `dist/`
2. Relancez le build
3. Vérifiez que tous les fichiers source sont présents

### L'exécutable ne se lance pas
- Testez sur une machine Windows propre
- Vérifiez les antivirus (peuvent bloquer les .exe générés)
- Utilisez `--debug` dans la commande PyInstaller

## 📊 Performances

- **Temps de build** : 1-3 minutes
- **Taille finale** : ~20 MB
- **Temps de lancement** : 2-5 secondes (premier lancement plus lent)

## 🔄 Mise à jour

Pour mettre à jour l'exécutable :
1. Modifiez le code source
2. Relancez `build.bat` ou `python build_exe.py`
3. Redistribuez le nouveau `WigorViewer.exe`

---

**💡 Astuce :** Créez un raccourci vers `WigorViewer.exe` sur le Bureau pour un accès rapide !