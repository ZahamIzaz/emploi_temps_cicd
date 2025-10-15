#!/usr/bin/env python3
"""
Test rapide pour CI - Valide les imports et fonctions de base
"""
import sys
import os

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_imports():
    """Test que tous les modules principaux s'importent correctement"""
    try:
        print("🔍 Testing imports...")
        
        # Test imports des modules
        import src.main
        import src.cli  
        import src.wigor_api
        import src.timetable_parser
        import src.gui
        
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_basic_functionality():
    """Test des fonctions de base"""
    try:
        print("🔍 Testing basic functionality...")
        
        # Test parser avec HTML basique
        from src.timetable_parser import parse_wigor_html
        result = parse_wigor_html("<html><body></body></html>")
        assert isinstance(result, dict)
        assert "courses" in result
        
        # Test extraction de titre de page
        from src.wigor_api import extract_page_title
        title = extract_page_title("<html><head><title>Test</title></head></html>")
        assert title == "Test"
        
        # Test parsing de cookies
        from src.wigor_api import parse_cookie_header
        cookies = parse_cookie_header("session=123; csrf=abc")
        assert isinstance(cookies, dict)
        
        print("✅ Basic functionality tests passed")
        return True
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        return False


def main():
    """Point d'entrée principal"""
    print("🚀 Starting CI smoke tests...")
    
    tests = [
        test_imports,
        test_basic_functionality,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("✅ All smoke tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()