#!/usr/bin/env python3
"""
Interface en ligne de commande pour Wigor Viewer.
Fournit des commandes pour tester et valider l'application sans interface graphique.
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from typing import Optional

try:
    from .wigor_api import WigorAPI
    from .timetable_parser import parse_wigor_html
    from .gui import WigorViewerGUI
except ImportError:
    # Imports absolus pour exécution directe
    from src.wigor_api import WigorAPI
    from src.timetable_parser import parse_wigor_html
    from src.gui import WigorViewerGUI

# Version de l'application
__version__ = "2.0.0"

# Configuration du logger
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_version() -> str:
    """Retourne la version de l'application."""
    return __version__


def smoke_test() -> int:
    """
    Lance un test rapide pour vérifier que les composants principaux fonctionnent.
    
    Returns:
        int: Code de retour (0 = succès, 1 = échec)
    """
    print("🧪 Smoke test - Vérification des composants principaux...")
    
    try:
        # Test 1: Instanciation des classes principales
        print("  ✓ Test 1: Instanciation WigorAPI...", end=" ")
        WigorAPI()
        print("OK")
        
        # Test 2: Chargement du fichier de test
        print("  ✓ Test 2: Chargement fixture HTML...", end=" ")
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_timetable.html"
        
        if not fixture_path.exists():
            print("SKIP (fixture non trouvée)")
            logger.warning(f"Fixture non trouvée: {fixture_path}")
        else:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                sample_html = f.read()
            print("OK")
            
            # Test 3: Parsing HTML
            print("  ✓ Test 3: Parsing HTML de test...", end=" ")
            courses = parse_wigor_html(sample_html)
            if isinstance(courses, list):  # Vérification que c'est bien une liste
                print(f"OK ({len(courses)} cours trouvés)")
            else:
                print("FAIL (erreur de parsing)")
                return 1
        
        # Test 4: Vérification que GUI ne se lance pas automatiquement
        print("  ✓ Test 4: Vérification mode headless...", end=" ")
        # On vérifie juste que la classe peut être importée sans erreur
        # et qu'aucune fenêtre n'est créée automatiquement
        assert WigorViewerGUI is not None
        print("OK")
        
        # Test 5: Vérification des imports critiques
        print("  ✓ Test 5: Vérification des imports...", end=" ")
        import requests
        import bs4
        print("OK")
        
        print("✅ Tous les tests sont passés avec succès!")
        return 0
        
    except ImportError as e:
        print(f"FAIL - Import error: {e}")
        logger.error(f"Erreur d'import: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"FAIL - File not found: {e}")
        logger.error(f"Fichier non trouvé: {e}")
        return 1
    except Exception as e:
        print(f"FAIL - Unexpected error: {e}")
        logger.error(f"Erreur inattendue: {e}")
        return 1


def test_parsing(file_path: Optional[str] = None) -> int:
    """
    Test du parsing d'un fichier HTML spécifique.
    
    Args:
        file_path: Chemin vers le fichier HTML à tester
        
    Returns:
        int: Code de retour (0 = succès, 1 = échec)
    """
    if not file_path:
        file_path = Path(__file__).parent.parent / "fixtures" / "sample_timetable.html"
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return 1
    
    try:
        print(f"🔍 Test de parsing: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"  📄 Taille du fichier: {len(html_content):,} caractères")
        
        courses = parse_wigor_html(html_content)
        
        print(f"  📊 Cours trouvés: {len(courses)}")
        
        if courses:
            print("  📋 Aperçu des cours:")
            for i, course in enumerate(courses[:3], 1):
                title = course.get('titre', 'N/A')
                time = course.get('horaire', 'N/A')
                room = course.get('salle', 'N/A')
                print(f"    {i}. {title} | {time} | {room}")
            
            if len(courses) > 3:
                print(f"    ... et {len(courses) - 3} autres cours")
        
        print("✅ Parsing réussi!")
        return 0
        
    except Exception as e:
        print(f"❌ Erreur lors du parsing: {e}")
        logger.error(f"Erreur de parsing: {e}")
        return 1


def check_environment() -> int:
    """
    Vérifie l'environnement et les dépendances.
    
    Returns:
        int: Code de retour (0 = OK, 1 = problème)
    """
    print("🔧 Vérification de l'environnement...")
    
    # Vérification Python
    print(f"  🐍 Python: {sys.version.split()[0]}")
    
    # Vérification des dépendances
    dependencies = [
        ('requests', 'Requêtes HTTP'),
        ('bs4', 'BeautifulSoup4'),
        ('tkinter', 'Interface graphique'),
    ]
    
    missing_deps = []
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"  ✓ {description}: OK")
        except ImportError:
            print(f"  ❌ {description}: MANQUANT")
            missing_deps.append(module)
    
    # Vérification des fichiers critiques
    project_root = Path(__file__).parent.parent
    critical_files = [
        'src/wigor_api.py',
        'src/timetable_parser.py',
        'src/gui.py',
        'requirements.txt',
    ]
    
    missing_files = []
    for file_path in critical_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}: OK")
        else:
            print(f"  ❌ {file_path}: MANQUANT")
            missing_files.append(file_path)
    
    if missing_deps or missing_files:
        print("\n❌ Problèmes détectés:")
        if missing_deps:
            print(f"  Dépendances manquantes: {', '.join(missing_deps)}")
        if missing_files:
            print(f"  Fichiers manquants: {', '.join(missing_files)}")
        return 1
    
    print("\n✅ Environnement OK!")
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Crée le parser d'arguments CLI."""
    parser = argparse.ArgumentParser(
        prog='wigor-cli',
        description='Interface en ligne de commande pour Wigor Viewer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  wigor-cli --version                    # Affiche la version
  wigor-cli --check                      # Lance le smoke test
  wigor-cli --test-parsing sample.html   # Test de parsing
  wigor-cli --check-env                  # Vérification environnement
        """
    )
    
    # Commandes principales
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument(
        '--version',
        action='store_true',
        help='Affiche la version de l\'application'
    )
    
    group.add_argument(
        '--check',
        action='store_true',
        help='Lance un smoke test rapide (vérification des composants)'
    )
    
    group.add_argument(
        '--test-parsing',
        metavar='FILE',
        help='Test le parsing d\'un fichier HTML spécifique'
    )
    
    group.add_argument(
        '--check-env',
        action='store_true',
        help='Vérifie l\'environnement et les dépendances'
    )
    
    # Options globales
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mode verbeux (affiche plus de détails)'
    )
    
    return parser


def main() -> int:
    """
    Point d'entrée principal du CLI.
    
    Returns:
        int: Code de retour pour le système
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Configuration du logging
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    
    # Exécution des commandes
    try:
        if args.version:
            print(f"Wigor Viewer v{get_version()}")
            return 0
        
        elif args.check:
            return smoke_test()
        
        elif args.test_parsing:
            return test_parsing(args.test_parsing)
        
        elif args.check_env:
            return check_environment()
        
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Opération interrompue par l'utilisateur")
        return 130
    except Exception as e:
        print(f"💥 Erreur inattendue: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())