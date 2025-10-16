#!/usr/bin/env python3
"""
Test complet des nouvelles fonctionnalités d'authentification Wigor Viewer.

Ce script teste toutes les nouvelles fonctionnalités implémentées :
- Interface GUI avec nouveaux champs
- Fonction login_with_credentials()
- Gestion des erreurs
- Extraction et manipulation des cookies

Usage:
    python test_integration.py
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

import requests

# Ajouter le dossier src au Python path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


# Test des imports
def test_imports():
    """Test que tous les modules s'importent correctement."""
    print("🔍 Test des imports...")
    try:
        # Import des modules principaux
        import gui
        import timetable_parser
        import wigor_api

        # Import des modules d'authentification
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "auth"))
        import cookies_auth

        print("✅ Tous les imports fonctionnent")
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False


def test_gui_creation():
    """Test la création de l'interface graphique."""
    print("\n🖥️ Test de création GUI...")
    try:
        import gui

        # Créer la fenêtre principale
        root = tk.Tk()
        app = gui.WigorViewerGUI(root)

        # Vérifier que les nouveaux champs existent
        required_widgets = ["username_entry", "password_entry", "login_button", "status_label"]

        missing_widgets = []
        for widget_name in required_widgets:
            if not hasattr(app, widget_name):
                missing_widgets.append(widget_name)

        root.destroy()  # Fermer la fenêtre de test

        if missing_widgets:
            print(f"❌ Widgets manquants: {missing_widgets}")
            return False
        else:
            print("✅ Interface GUI créée avec tous les nouveaux champs")
            return True

    except Exception as e:
        print(f"❌ Erreur création GUI: {e}")
        return False


def test_login_function_exists():
    """Test que la nouvelle fonction de login existe."""
    print("\n🔐 Test existence fonction login_with_credentials...")
    try:
        import wigor_api

        if hasattr(wigor_api, "login_with_credentials"):
            print("✅ Fonction login_with_credentials trouvée")

            # Test signature de la fonction
            import inspect

            sig = inspect.signature(wigor_api.login_with_credentials)
            params = list(sig.parameters.keys())

            expected_params = ["username", "password", "url"]
            if all(param in params for param in expected_params):
                print("✅ Signature de fonction correcte")
                return True
            else:
                print(f"❌ Paramètres manquants. Attendus: {expected_params}, Trouvés: {params}")
                return False
        else:
            print("❌ Fonction login_with_credentials non trouvée")
            return False

    except Exception as e:
        print(f"❌ Erreur test fonction: {e}")
        return False


def test_utility_functions():
    """Test les fonctions utilitaires d'authentification."""
    print("\n🛠️ Test fonctions utilitaires...")
    try:
        import wigor_api

        # Fonctions utilitaires à vérifier
        utility_functions = [
            "_find_login_form",
            "_extract_form_data",
            "_get_form_action",
            "_extract_cookies_string",
        ]

        missing_functions = []
        for func_name in utility_functions:
            if not hasattr(wigor_api, func_name):
                missing_functions.append(func_name)

        if missing_functions:
            print(f"❌ Fonctions utilitaires manquantes: {missing_functions}")
            return False
        else:
            print("✅ Toutes les fonctions utilitaires trouvées")
            return True

    except Exception as e:
        print(f"❌ Erreur test utilitaires: {e}")
        return False


def test_mock_login():
    """Test simulation de login (sans vrais identifiants)."""
    print("\n🧪 Test simulation login...")
    try:
        import wigor_api

        # Test avec des identifiants factices et une URL invalide
        result = wigor_api.login_with_credentials(
            username="test_user", password="test_pass", url="https://invalid-url-for-testing.com"
        )

        # Vérifier la structure de la réponse
        expected_keys = ["success", "error", "status_code"]
        if all(key in result for key in expected_keys):
            print("✅ Structure de réponse correcte")

            if not result["success"]:
                print("✅ Échec attendu avec URL invalide")
                return True
            else:
                print("❌ Succès inattendu avec URL invalide")
                return False
        else:
            print(f"❌ Structure de réponse incorrecte: {result}")
            return False

    except Exception as e:
        print(f"❌ Erreur test simulation: {e}")
        return False


def test_cookies_functions():
    """Test les fonctions de gestion des cookies."""
    print("\n🍪 Test fonctions cookies...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "auth"))
        import cookies_auth

        # Test avec un cookie factice
        fake_cookie = "ASP.NET_SessionId=test123; .DotNetCasClientAuth=auth456"
        session = cookies_auth.build_session_from_cookie_header(fake_cookie)

        if session and hasattr(session, "cookies"):
            print("✅ Session créée à partir des cookies")

            # Test de validation
            is_auth = cookies_auth.is_authenticated(session, "https://test.com")
            print(f"✅ Fonction de validation testée (résultat: {is_auth})")
            return True
        else:
            print("❌ Échec création session")
            return False

    except Exception as e:
        print(f"❌ Erreur test cookies: {e}")
        return False


def run_all_tests():
    """Exécute tous les tests et affiche un résumé."""
    print("🚀 TESTS D'INTÉGRATION WIGOR VIEWER")
    print("=" * 50)

    tests = [
        ("Imports des modules", test_imports),
        ("Création interface GUI", test_gui_creation),
        ("Fonction de login", test_login_function_exists),
        ("Fonctions utilitaires", test_utility_functions),
        ("Simulation de login", test_mock_login),
        ("Gestion des cookies", test_cookies_functions),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Erreur inattendue dans '{test_name}': {e}")
            results.append((test_name, False))

    # Affichage du résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1

    print(f"\n🎯 Résultat: {passed}/{total} tests réussis")

    if passed == total:
        print("🎉 Tous les tests passent ! L'application est prête.")
    else:
        print("⚠️ Certains tests échouent. Vérifiez les erreurs ci-dessus.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()

    if success:
        print("\n🚀 Voulez-vous lancer l'application ? (run.py)")
        print("🔍 Ou voir les nouvelles fonctionnalités ? (NOUVELLES_FONCTIONNALITES.md)")

    sys.exit(0 if success else 1)
