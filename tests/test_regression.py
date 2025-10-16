#!/usr/bin/env python3
"""
Tests de régression pour Wigor Viewer.
Utilise des snapshots JSON pour détecter les régressions dans le parsing.
"""

import json
import unittest
from pathlib import Path

# Import du parseur
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.timetable_parser import parse_wigor_html


class TestRegression(unittest.TestCase):
    """Tests de régression basés sur des snapshots."""

    def setUp(self):
        """Configuration des chemins de test."""
        self.tests_dir = Path(__file__).parent
        self.fixtures_dir = self.tests_dir / "fixtures"
        self.snapshots_dir = self.tests_dir / "snapshots"

    def test_sample_timetable_regression(self):
        """Test de régression sur l'exemple d'emploi du temps."""
        # Charger le fichier HTML de test
        fixture_path = self.fixtures_dir / "sample_timetable.html"
        self.assertTrue(fixture_path.exists(), f"Fixture non trouvée: {fixture_path}")

        with open(fixture_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Parser le contenu
        courses = parse_wigor_html(html_content)

        # Vérifier que c'est une liste
        self.assertIsInstance(courses, list, "Le parser doit retourner une liste")

        # Charger le snapshot attendu
        snapshot_path = self.snapshots_dir / "expected_timetable.json"

        if not snapshot_path.exists():
            # Si pas de snapshot, créer le premier
            print(f"Création du snapshot initial: {snapshot_path}")
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(courses, f, indent=2, ensure_ascii=False)
            self.skipTest("Snapshot initial créé")

        with open(snapshot_path, "r", encoding="utf-8") as f:
            expected_courses = json.load(f)

        # Comparer avec le snapshot
        self.assertEqual(
            len(courses),
            len(expected_courses),
            f"Nombre de cours différent. Attendu: {len(expected_courses)}, Obtenu: {len(courses)}",
        )

        # Comparaison détaillée (optionnelle si le format change)
        if courses != expected_courses:
            print("⚠️ Différence détectée avec le snapshot:")
            print(f"Attendu: {json.dumps(expected_courses, indent=2, ensure_ascii=False)}")
            print(f"Obtenu:  {json.dumps(courses, indent=2, ensure_ascii=False)}")

            # Ne pas échouer immédiatement, permettre la mise à jour manuelle
            self.fail("Régression détectée - le parsing a changé par rapport au snapshot")

    def test_empty_html_stability(self):
        """Test de stabilité avec HTML vide."""
        empty_html = "<html><body></body></html>"
        courses = parse_wigor_html(empty_html)

        self.assertIsInstance(courses, list)
        self.assertEqual(len(courses), 0, "HTML vide doit retourner une liste vide")

    def test_malformed_html_stability(self):
        """Test de stabilité avec HTML malformé."""
        malformed_html = "<html><body><div class='Case'>Cours sans structure</div></body></html>"

        # Ne doit pas crasher
        try:
            courses = parse_wigor_html(malformed_html)
            self.assertIsInstance(courses, list)
        except Exception as e:
            self.fail(f"Le parser ne doit pas crasher sur HTML malformé: {e}")


if __name__ == "__main__":
    unittest.main()
