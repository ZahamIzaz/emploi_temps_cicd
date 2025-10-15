# 🆕 NOUVELLES FONCTIONNALITÉS WIGOR VIEWER

## ✨ Authentification automatique avec identifiants

L'application Wigor Viewer a été enrichie avec de nouvelles fonctionnalités d'authentification automatique !

## 🖥️ Interface graphique améliorée

### Nouveaux champs ajoutés :
- ✅ **Champ Identifiant** : Saisie du nom d'utilisateur EPSI
- ✅ **Champ Mot de passe** : Saisie sécurisée (masquée)
- ✅ **Bouton "Se connecter avec identifiants"** : Authentification automatique
- ✅ **Indicateurs de statut** : Visual feedback pour chaque étape

### Organisation de l'interface :
```
┌─── URL Wigor ──────────────────────────┐
├─── AUTHENTIFICATION ──────────────────┤
│ • Identifiant                          │
│ • Mot de passe                         │
│ • [Se connecter avec identifiants] 🔐 │
├─── COOKIE MANUEL ─────────────────────┤
│ • Cookie (copié depuis Chrome)        │
│ • [Tester connexion] 🧪               │
├─── CHARGEMENT ────────────────────────┤
│ • [Charger mon emploi du temps] 📅    │
└────────────────────────────────────────┘
```

## ⚡ Fonctionnalité login_with_credentials

### Processus d'authentification automatique :

1. **Redirection initiale** : GET sur l'URL Wigor → redirection CAS
2. **Détection formulaire** : Analyse HTML pour trouver `<form>` avec champs login/password
3. **Extraction champs cachés** : Récupération automatique de :
   - `lt` (Login Ticket)
   - `execution` (Flow Execution Key)
   - `_eventId` (Event Identifier)
   - Tous autres champs `<input type="hidden">`
4. **Soumission POST** : Envoi des identifiants avec tous les champs requis
5. **Suivi redirections** : Navigation jusqu'à wigorservices.net
6. **Vérification succès** : Détection de "EDT -" ou "innerCase"
7. **Extraction cookies** : Récupération `ASP.NET_SessionId` et `.DotNetCasClientAuth`

### Gestion d'erreurs complète :
- ✅ **Codes HTTP** : Affichage du code d'erreur dans la barre de statut
- ✅ **Messages clairs** : "Identifiants incorrects", "Erreur de réseau", etc.
- ✅ **Logging détaillé** : Traçage de chaque étape pour debugging
- ✅ **Fallback gracieux** : Retour aux cookies manuels si échec

## 🔄 Workflow utilisateur optimisé

### Option 1: Authentification automatique (NOUVEAU)
```
1. Saisir URL Wigor
2. Saisir identifiant EPSI
3. Saisir mot de passe
4. Clic "Se connecter avec identifiants"
   ↓
5. Authentification automatique
6. Cookies remplis automatiquement
7. Clic "Charger mon emploi du temps"
```

### Option 2: Cookies manuels (existant)
```
1. Saisir URL Wigor
2. Copier cookies depuis Chrome
3. Clic "Tester connexion"
4. Clic "Charger mon emploi du temps"
```

## 🔧 Implémentation technique

### Nouveau fichier : `login_with_credentials()` dans wigor_api.py

```python
def login_with_credentials(username: str, password: str, url: str) -> Dict[str, Union[bool, str, requests.Session, int]]:
    """
    Se connecte à Wigor avec identifiant et mot de passe.
    
    Returns:
        Dict contenant:
            - success (bool): True si connexion réussie
            - session (requests.Session): Session authentifiée si succès
            - cookies_string (str): Cookies au format string si succès
            - error (str): Message d'erreur si échec
            - status_code (int): Code HTTP de la dernière réponse
    """
```

### Fonctions utilitaires ajoutées :
- `_find_login_form()` : Détection formulaire de connexion
- `_find_cas_login_url()` : Recherche URL CAS
- `_extract_form_data()` : Extraction champs formulaire + champs cachés
- `_get_form_action()` : Récupération URL d'action
- `_find_redirect_url()` : Suivi redirections JavaScript/meta
- `_extract_cookies_string()` : Conversion cookies session → string

## 🎯 Avantages utilisateur

1. **Plus besoin de manipuler les cookies** : Authentification directe
2. **Process simplifié** : Juste identifiant + mot de passe
3. **Sécurisé** : Pas de copie-coller de données sensibles
4. **Automatique** : Remplissage cookie automatique après connexion
5. **Fallback** : Option cookies manuels toujours disponible
6. **Feedback visuel** : Indicateurs de progression et d'erreur

## 🚀 Utilisation

### Lancer l'application :
```bash
python run.py
```

### Interface mise à jour :
1. **Saisir l'URL** de votre emploi du temps Wigor
2. **Saisir vos identifiants** EPSI (identifiant + mot de passe)
3. **Cliquer "Se connecter avec identifiants"**
4. **Attendre la confirmation** "Connecté ✅"
5. **Cliquer "Charger mon emploi du temps"**

### En cas d'erreur :
- Vérifier identifiants
- Consulter le code d'erreur affiché
- Utiliser l'option cookies manuels en fallback

## 📋 Compatibilité

- ✅ **CAS (Central Authentication Service)** : Support complet
- ✅ **Champs cachés** : Gestion automatique `lt`, `execution`, `_eventId`
- ✅ **Redirections multiples** : Suivi JavaScript et meta refresh
- ✅ **Sessions persistantes** : Réutilisation après authentification
- ✅ **Debug intégré** : Sauvegarde HTML pour diagnostic

---

**L'application Wigor Viewer est maintenant encore plus simple à utiliser ! 🎉**