"""
Point d'entrée principal de l'application wigor-viewer.
Ce fichier lance l'interface graphique ou exécute des tests en ligne de commande.
"""

import argparse
import logging
import os
import sys
from typing import Optional

try:
    from .gui import WigorViewerGUI
    from .timetable_parser import parse_wigor_html
    from .wigor_api import fetch_wigor_html
except ImportError:
    # Imports absolus pour exécution directe
    from src.gui import WigorViewerGUI
    from src.timetable_parser import parse_wigor_html
    from src.wigor_api import fetch_wigor_html

# Configuration du logger
logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """
    Configure le système de logging pour l'application.

    Args:
        level (str): Niveau de logging (DEBUG, INFO, WARNING, ERROR)
        log_file (Optional[str]): Fichier de log optionnel
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configuration basique
    handlers = [logging.StreamHandler(sys.stdout)]

    # Ajouter un fichier de log si spécifié
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )

    logger.info(f"Logging configuré au niveau {level}")


def test_mode(url: str, cookie: str) -> int:
    """
    Mode test : télécharge l'HTML et affiche le nombre de cours.

    Args:
        url (str): URL de la page Wigor
        cookie (str): Cookie d'authentification

    Returns:
        int: Code de retour (0 = succès, 1 = erreur)
    """
    print("🔍 Mode test activé - Téléchargement et analyse de l'emploi du temps")
    print(f"URL: {url}")
    print("=" * 60)

    try:
        # Télécharger le HTML
        print("📥 Téléchargement du HTML...")
        html_content = fetch_wigor_html(url, cookie)
        print(f"✅ HTML téléchargé ({len(html_content):,} caractères)")

        # Parser les cours
        print("🔍 Analyse des cours...")
        courses = parse_wigor_html(html_content)

        # Afficher les résultats
        print(f"📊 Nombre de cours trouvés: {len(courses)}")

        if courses:
            # Statistiques par jour
            days_stats = {}
            for course in courses:
                day = course.get("jour", "Jour inconnu")
                days_stats[day] = days_stats.get(day, 0) + 1

            print("\n📅 Répartition par jour:")
            for day, count in days_stats.items():
                print(f"  • {day}: {count} cours")

            # Afficher quelques exemples
            print(f"\n📋 Aperçu des cours (max 5):")
            for i, course in enumerate(courses[:5]):
                print(f"  {i+1}. {course.get('titre', 'N/A')} - {course.get('horaire', 'N/A')}")
                print(
                    f"     Salle: {course.get('salle', 'N/A')} | Prof: {course.get('prof', 'N/A')}"
                )

            if len(courses) > 5:
                print(f"     ... et {len(courses) - 5} autres cours")
        else:
            print("⚠️  Aucun cours trouvé - vérifiez l'URL et les cookies")

        print("\n✅ Test terminé avec succès")
        return 0

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        logger.error(f"Erreur en mode test: {e}")
        return 1


def gui_mode():
    """
    Lance l'interface graphique.
    """
    try:
        logger.info("Lancement de l'interface graphique")
        app = WigorViewerGUI()
        app.run()
        logger.info("Interface graphique fermée")
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'interface: {e}")
        print(f"❌ Impossible de lancer l'interface graphique: {e}")
        sys.exit(1)


def parse_arguments():
    """
    Parse les arguments de ligne de commande.

    Returns:
        argparse.Namespace: Arguments parsés
    """
    parser = argparse.ArgumentParser(
        description="Wigor Viewer - Afficheur d'emploi du temps EPSI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  # Lancer l'interface graphique (par défaut)
  python -m wigor_viewer.src.main

  # Mode test avec URL et cookies
  python -m wigor_viewer.src.main --test --url "https://..." --cookie "ASP.NET_SessionId=..."

  # Avec logging debug
  python -m wigor_viewer.src.main --log-level DEBUG

  # Sauvegarder les logs dans un fichier
  python -m wigor_viewer.src.main --log-file wigor.log
        """,
    )

    # Mode de fonctionnement
    parser.add_argument(
        "--test",
        action="store_true",
        help="Mode test : télécharge et analyse sans interface graphique",
    )

    # Paramètres pour le mode test
    parser.add_argument("--url", type=str, help="URL de la page Wigor (requis en mode test)")

    parser.add_argument(
        "--cookie", type=str, help="Cookie d'authentification (requis en mode test)"
    )

    # Options de logging
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Niveau de logging (défaut: INFO)",
    )

    parser.add_argument("--log-file", type=str, help="Fichier de sortie pour les logs (optionnel)")

    return parser.parse_args()


def validate_test_args(args):
    """
    Valide les arguments requis pour le mode test.

    Args:
        args: Arguments parsés

    Returns:
        bool: True si valide, False sinon
    """
    if not args.url:
        print("❌ Erreur: --url est requis en mode test")
        return False

    if not args.cookie:
        print("❌ Erreur: --cookie est requis en mode test")
        return False

    return True


def main():
    """
    Fonction principale de l'application.
    """
    # Parser les arguments
    args = parse_arguments()

    # Configuration du logging
    setup_logging(level=args.log_level, log_file=args.log_file)

    logger.info("Démarrage de Wigor Viewer")
    logger.info(f"Arguments: {vars(args)}")

    try:
        if args.test:
            # Mode test
            logger.info("Mode test sélectionné")

            if not validate_test_args(args):
                sys.exit(1)

            exit_code = test_mode(args.url, args.cookie)
            sys.exit(exit_code)
        else:
            # Mode interface graphique (par défaut)
            logger.info("Mode interface graphique sélectionné")
            # Vérifier qu'on n'est pas en mode CI/batch
            if (
                os.environ.get("CI")
                or os.environ.get("DISPLAY") == ""
                or os.environ.get("HEADLESS")
            ):
                logger.warning("Mode CI/headless détecté - interface graphique désactivée")
                print("⚠️  Mode CI/headless détecté. Utilisez --help pour les options CLI.")
                print("   Exemple: python -m src.cli --check")
                sys.exit(0)
            gui_mode()

    except KeyboardInterrupt:
        logger.info("Interruption utilisateur (Ctrl+C)")
        print("\n🛑 Application interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        print(f"💥 Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
