# 📖 GUIDE D'UTILISATION - WIGOR VIEWER v2.0

## 🎯 Vue d'ensemble

Wigor Viewer est un outil Python qui permet de récupérer et afficher votre emploi du temps EPSI depuis le système Wigor. 

**✨ NOUVEAUTÉ v2.0 :** Authentification automatique avec vos identifiants EPSI !

---

## 🚀 Installation et lancement

### 1. Prérequis
```bash
# Vérifier Python (version 3.7+)
python --version

# Installer les dépendances
pip install requests beautifulsoup4 lxml
```

### 2. Lancement de l'application
```bash
# Interface graphique (recommandé)
python run.py

# Ou directement
python src/main.py --gui

# Mode CLI pour tests
python src/main.py --test
```

### 3. Test de l'installation
```bash
# Vérifier que tout fonctionne
python test_integration.py
```

---

## 🖥️ Utilisation de l'interface graphique

### Écran principal
```
┌─────────────── WIGOR VIEWER ───────────────┐
│                                            │
│ 📡 URL Wigor                              │
│ ┌────────────────────────────────────────┐ │
│ │ https://wigor.net/path/to/timetable    │ │
│ └────────────────────────────────────────┘ │
│                                            │
│ 🔐 AUTHENTIFICATION AUTOMATIQUE           │
│ ┌─ Identifiant ─────────┐ ┌─ Mot de passe ┐│
│ │ votre.nom            │ │ ••••••••••    ││
│ └──────────────────────┘ └───────────────┘│
│ [Se connecter avec identifiants] 🔑       │
│                                            │
│ 🍪 AUTHENTIFICATION MANUELLE              │
│ ┌────────────────────────────────────────┐ │
│ │ ASP.NET_SessionId=...; .DotNet...     │ │
│ └────────────────────────────────────────┘ │
│ [Tester la connexion] 🧪                  │
│                                            │
│ 📅 CHARGEMENT                             │
│ [Charger mon emploi du temps] 📋          │
│                                            │
│ 📊 Status: Prêt                          │
└────────────────────────────────────────────┘
```

---

## 🔧 Méthodes d'authentification

### 🆕 Méthode 1 : Identifiants EPSI (Recommandée)

**Avantages :** Simple, sécurisé, automatique

1. **Récupérer l'URL de votre emploi du temps :**
   - Se connecter à [wigor.net](https://wigor.net)
   - Naviguer vers votre emploi du temps
   - Copier l'URL complète (doit contenir `wigorservices.net`)

2. **Dans l'application :**
   - Coller l'URL dans le champ "URL Wigor"
   - Saisir votre **identifiant EPSI** (ex: prenom.nom)
   - Saisir votre **mot de passe EPSI**
   - Cliquer "**Se connecter avec identifiants**" 🔑

3. **Attendre la confirmation :**
   - Status passe à "Connexion en cours..." ⏳
   - Puis "Connecté ✅" si succès
   - Ou message d'erreur si échec ❌

4. **Charger l'emploi du temps :**
   - Cliquer "**Charger mon emploi du temps**" 📋

### Méthode 2 : Cookies manuels (Fallback)

**Quand utiliser :** Si l'authentification automatique échoue

1. **Récupérer les cookies depuis Chrome :**
   - Ouvrir Chrome et se connecter à Wigor
   - Aller sur votre emploi du temps
   - `F12` → Onglet "Application" → "Cookies" → "wigorservices.net"
   - Copier les valeurs de `ASP.NET_SessionId` et `.DotNetCasClientAuth`

2. **Format attendu :**
   ```
   ASP.NET_SessionId=abc123def456; .DotNetCasClientAuth=xyz789uvw
   ```

3. **Dans l'application :**
   - Coller dans le champ "Cookie"
   - Cliquer "**Tester la connexion**" 🧪
   - Si OK, cliquer "**Charger mon emploi du temps**" 📋

---

## 📋 Formats de sortie

### Format console
```
🗓️ EMPLOI DU TEMPS - Semaine du XX/XX/XXXX

📅 LUNDI XX/XX
  🕘 08:30-10:30 | Développement Web | Salle A101 | M. DUPONT
  🕙 10:45-12:45 | Base de données  | Salle B205 | Mme MARTIN

📅 MARDI XX/XX  
  🕘 09:00-11:00 | Algorithmique    | Salle C301 | M. BERNARD
  
📊 RÉSUMÉ: X cours trouvés cette semaine
```

### Interface graphique
- **Tableau structuré** avec colonnes : Jour, Heure, Matière, Salle, Professeur
- **Codes couleur** pour différents types de cours
- **Scroll automatique** pour les longues semaines
- **Rafraîchissement** en temps réel

---

## 🐛 Résolution des problèmes

### Erreurs d'authentification automatique

| Erreur | Cause probable | Solution |
|--------|---------------|----------|
| `Identifiants incorrects` | Login/password erroné | Vérifier identifiants EPSI |
| `Erreur de réseau (404)` | URL Wigor invalide | Vérifier l'URL copiée |
| `Erreur de réseau (500)` | Serveur Wigor indisponible | Réessayer plus tard |
| `Formulaire de login introuvable` | Page non CAS | Vérifier que l'URL redirige vers CAS |
| `Cookies non extraits` | Échec redirection finale | Utiliser cookies manuels |

### Erreurs générales

**URL invalide :**
```
❌ Erreur: URL non valide
✅ Solution: Vérifier le format https://wigorservices.net/...
```

**Pas de cours trouvés :**
```
❌ Erreur: Aucun cours trouvé
✅ Solution: 
   - Vérifier la semaine affichée sur Wigor
   - S'assurer d'être sur la bonne vue (emploi du temps étudiant)
```

**Erreur de connexion :**
```
❌ Erreur: Impossible de se connecter
✅ Solution:
   - Vérifier la connexion Internet
   - Tester manuellement sur wigor.net
   - Utiliser les cookies manuels
```

### Debug avancé

**Activer les logs détaillés :**
```bash
# Mode debug complet
python src/main.py --test --verbose
```

**Fichiers de debug générés :**
- `debug_wigor_YYYYMMDD_HHMMSS.html` : Page HTML téléchargée
- Logs console avec timestamps et détails HTTP

---

## 🔧 Configuration avancée

### Variables d'environnement optionnelles
```bash
# Timeout des requêtes (défaut: 30s)
export WIGOR_TIMEOUT=60

# User-Agent personnalisé
export WIGOR_USER_AGENT="Custom Browser"

# Dossier de debug
export WIGOR_DEBUG_DIR="/path/to/debug"
```

### Personnalisation GUI
```python
# Dans src/gui.py, modifier les constantes :
WINDOW_WIDTH = 800    # Largeur fenêtre
WINDOW_HEIGHT = 600   # Hauteur fenêtre
FONT_SIZE = 12        # Taille police
```

---

## 🧪 Tests et validation

### Tests unitaires
```bash
# Tests du parser HTML (14 tests)
python -m pytest tests/test_parser.py -v

# Tests avec couverture
python -m pytest tests/test_parser.py --cov=src
```

### Tests d'intégration
```bash
# Test complet de l'application
python test_integration.py

# Test GUI seulement
python -c "import src.gui; print('GUI OK')"

# Test API seulement  
python -c "import src.wigor_api; print('API OK')"
```

### Tests manuels
```bash
# Mode test interactif
python src/main.py --test

# Test avec URL spécifique
python src/main.py --test --url "https://..."
```

---

## 📚 Architecture technique

### Structure des fichiers
```
wigor_viewer/
├── 📁 src/                     # Code source principal
│   ├── main.py                 # Point d'entrée CLI
│   ├── gui.py                  # Interface graphique Tkinter
│   ├── wigor_api.py           # Client HTTP + auth automatique  
│   └── timetable_parser.py     # Parser HTML emploi du temps
├── 📁 auth/                    # Modules d'authentification
│   └── cookies_auth.py         # Gestion sessions et cookies
├── 📁 tests/                   # Tests unitaires
│   └── test_parser.py          # Tests du parser (14 tests)
├── run.py                      # Launcher simplifié
├── test_integration.py         # Tests d'intégration
├── README.md                   # Documentation principale
└── NOUVELLES_FONCTIONNALITES.md # Guide v2.0
```

### Flux d'authentification automatique
```
[URL Wigor] → [Redirection CAS] → [Formulaire Login] 
     ↓              ↓                    ↓
[GET Request] → [Analyse HTML] → [Extract form fields]
     ↓              ↓                    ↓  
[POST Login] → [Suivi redirections] → [Extract cookies]
     ↓              ↓                    ↓
[Validation] → [Session créée] → [Prêt pour emploi du temps]
```

### Dépendances
- **requests** : HTTP client avec support sessions
- **beautifulsoup4** : Parsing HTML robuste  
- **lxml** : Parser XML/HTML performant
- **tkinter** : Interface graphique (inclus avec Python)
- **pytest** : Framework de tests (dev seulement)

---

## 🎯 Conseils d'utilisation

### 🔥 Bonnes pratiques

1. **Toujours utiliser l'authentification automatique en premier**
   - Plus simple et sécurisé
   - Cookies générés automatiquement
   - Pas de manipulation manuelle

2. **Garder l'URL Wigor** 
   - Sauvegarder l'URL de votre emploi du temps
   - Elle ne change généralement pas
   - Permet un accès rapide

3. **Tester la connexion avant de charger**
   - Utiliser "Tester la connexion" en cas de doute
   - Évite les téléchargements inutiles
   - Confirme l'authentification

### ⚡ Raccourcis et astuces

- **Ctrl+C** dans la console pour arrêter l'application
- **Enter** dans les champs texte pour valider
- **Tab** pour naviguer entre les champs
- Les **mots de passe sont masqués** pour la sécurité
- L'application **mémorise l'URL** entre les sessions

### 🎨 Interface utilisateur

- **Couleurs des statuts :**
  - 🟢 Vert : Succès, connecté
  - 🟡 Orange : En cours, chargement  
  - 🔴 Rouge : Erreur, échec
  - ⚪ Gris : Neutre, prêt

- **Icônes dans les boutons :**
  - 🔑 Se connecter avec identifiants
  - 🧪 Tester la connexion  
  - 📋 Charger emploi du temps
  - 🔄 Rafraîchir/recharger

---

## ❓ FAQ

**Q: Mes identifiants ne fonctionnent pas**  
A: Vérifiez qu'ils sont identiques à ceux utilisés sur le portail EPSI. Testez d'abord sur wigor.net manuellement.

**Q: L'URL de mon emploi du temps est-elle correcte ?**  
A: Elle doit contenir `wigorservices.net` et pointer vers votre emploi du temps personnel.

**Q: Puis-je utiliser l'application sans Internet ?**  
A: Non, l'application a besoin d'Internet pour se connecter aux serveurs Wigor.

**Q: Les cookies expirent-ils ?**  
A: Oui, généralement après quelques heures. Utilisez l'authentification automatique pour les renouveler.

**Q: L'application fonctionne-t-elle sur Mac/Linux ?**  
A: Oui, Python et Tkinter sont multiplateformes. Adaptez juste les commandes shell si nécessaire.

---

## 🔮 Fonctionnalités futures

- [ ] **Cache local** des emplois du temps
- [ ] **Notifications** de changements d'emploi du temps  
- [ ] **Export** vers calendrier (iCal, Google Calendar)
- [ ] **Thèmes visuels** personnalisables
- [ ] **Multi-utilisateurs** dans une même session
- [ ] **API REST** pour intégrations tierces

---

*Wigor Viewer v2.0 - Développé pour simplifier l'accès aux emplois du temps EPSI 🎓*