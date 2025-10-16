#!/usr/bin/env python3
"""
Test rapide pour CI - Valide les imports et fonctions de base
"""
import os
import sys

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_imports():
    """Test que tous les modules principaux s'importent correctement"""
    print("🔍 Testing imports...")

    # Test imports des modules
    import src.cli
    import src.gui
    import src.main
    import src.timetable_parser
    import src.wigor_api

    print("✅ All imports successful")
    assert True  # Test passé si on arrive ici


def test_basic_functionality():
    """Test des fonctions de base"""
    print("🔍 Testing basic functionality...")

    # Test parser avec HTML basique
    from src.timetable_parser import parse_wigor_html

    result = parse_wigor_html("<html><body></body></html>")
    # Le parser retourne une liste de cours vide pour HTML vide
    assert isinstance(result, list)

    # Test extraction de titre de page
    from src.wigor_api import extract_page_title

    title = extract_page_title("<html><head><title>Test</title></head></html>")
    assert title == "Test"

    # Test parsing de cookies
    from src.wigor_api import parse_cookie_header

    cookies = parse_cookie_header("session=123; csrf=abc")
    assert isinstance(cookies, dict)

    print("✅ Basic functionality tests passed")


def main():
    """Point d'entrée principal"""
    print("🚀 Starting CI smoke tests...")

    try:
        test_imports()
        test_basic_functionality()
        print("✅ All smoke tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
