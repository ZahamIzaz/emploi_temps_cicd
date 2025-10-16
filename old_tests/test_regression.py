"""
Tests de non-régression pour le parsing des emplois du temps.
Vérifie que le parser produit toujours le même résultat pour des fixtures données.
"""

import json
import unittest
from pathlib import Path
from pprint import pformat
from typing import Any, Dict, List

try:
    from src.timetable_parser import parse_wigor_html
except ImportError:
    # Import pour tests exécutés depuis le répertoire racine
    import sys

    sys.path.append(".")
    from src.timetable_parser import parse_wigor_html


class TestTimetableRegression(unittest.TestCase):
    """Tests de non-régression pour le parsing d'emploi du temps."""

    def setUp(self):
        """Configuration des chemins de fichiers."""
        self.project_root = Path(__file__).parent
        self.fixtures_dir = self.project_root / "fixtures"
        self.snapshots_dir = self.project_root / "tests" / "snapshots"

        # Fichiers de test
        self.sample_html = self.fixtures_dir / "sample_timetable.html"
        self.expected_json = self.snapshots_dir / "expected_timetable.json"

    def load_fixture(self, filename: str) -> str:
        """
        Charge une fixture HTML.

        Args:
            filename: Nom du fichier de fixture

        Returns:
            str: Contenu HTML de la fixture
        """
        fixture_path = self.fixtures_dir / filename
        self.assertTrue(fixture_path.exists(), f"Fixture non trouvée: {fixture_path}")

        with open(fixture_path, "r", encoding="utf-8") as f:
            return f.read()

    def load_expected_result(self, filename: str) -> List[Dict[str, Any]]:
        """
        Charge le résultat attendu depuis un snapshot JSON.

        Args:
            filename: Nom du fichier snapshot

        Returns:
            List[Dict[str, Any]]: Résultat attendu
        """
        snapshot_path = self.snapshots_dir / filename
        self.assertTrue(snapshot_path.exists(), f"Snapshot non trouvé: {snapshot_path}")

        with open(snapshot_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_actual_result(self, result: List[Dict[str, Any]], filename: str):
        """
        Sauvegarde le résultat actuel pour débogage.

        Args:
            result: Résultat actuel du parsing
            filename: Nom du fichier de sauvegarde
        """
        actual_path = self.snapshots_dir / f"actual_{filename}"
        with open(actual_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Résultat actuel sauvé dans: {actual_path}")

    def format_diff_message(self, expected: List, actual: List) -> str:
        """
        Formate un message d'erreur détaillé pour les différences.

        Args:
            expected: Résultat attendu
            actual: Résultat actuel

        Returns:
            str: Message d'erreur formaté
        """
        message_parts = [
            "❌ Le résultat du parsing ne correspond pas au snapshot attendu!",
            "",
            "📊 Statistiques:",
            f"  • Attendu: {len(expected)} cours",
            f"  • Obtenu: {len(actual)} cours",
            "",
        ]

        # Comparaison simple des longueurs
        if len(expected) != len(actual):
            message_parts.extend(
                [
                    "📏 Différence de nombre de cours:",
                    f"  Attendu {len(expected)} cours, obtenu {len(actual)} cours",
                    "",
                ]
            )

        # Afficher les cours attendus
        if expected:
            message_parts.extend(["📋 Cours attendus:", ""])
            for i, course in enumerate(expected):
                summary = self._format_course_summary(course)
                message_parts.append(f"  [{i}] {summary}")
            message_parts.append("")

        # Afficher les cours obtenus
        if actual:
            message_parts.extend(["� Cours obtenus:", ""])
            for i, course in enumerate(actual):
                summary = self._format_course_summary(course)
                message_parts.append(f"  [{i}] {summary}")
            message_parts.append("")

        # Comparaison détaillée si même nombre d'éléments
        if len(expected) == len(actual) and len(expected) > 0:
            message_parts.extend(["🔍 Différences détaillées:", ""])
            for i, (exp_course, act_course) in enumerate(zip(expected, actual)):
                if exp_course != act_course:
                    message_parts.append(f"  Cours {i}:")
                    message_parts.append(f"    Attendu: {pformat(exp_course, width=80)}")
                    message_parts.append(f"    Obtenu:  {pformat(act_course, width=80)}")
                    message_parts.append("")

        message_parts.extend(
            [
                "🔧 Actions possibles:",
                "  1. Vérifier que les changements sont intentionnels",
                "  2. Mettre à jour le snapshot si le nouveau format est correct:",
                f"     copy tests\\snapshots\\actual_expected_timetable.json {self.expected_json}",
                "  3. Corriger le parser si les changements sont des régressions",
                "",
            ]
        )

        return "\n".join(message_parts)

    def _format_course_summary(self, course: Dict[str, Any]) -> str:
        """
        Formate un résumé lisible d'un cours.

        Args:
            course: Dictionnaire représentant un cours

        Returns:
            str: Résumé du cours
        """
        titre = course.get("titre", "N/A")
        horaire = course.get("horaire", course.get("heure_debut", "N/A"))
        salle = course.get("salle", "N/A")
        prof = course.get("prof", "N/A")

        return f"{titre} | {horaire} | {salle} | {prof}"

    def test_sample_timetable_parsing(self):
        """
        Test de non-régression principal pour le parsing de sample_timetable.html.

        Ce test vérifie que le parser produit exactement le même résultat
        que le snapshot enregistré. Toute modification du format de sortie
        du parser sera détectée.
        """
        # Charger la fixture HTML
        html_content = self.load_fixture("sample_timetable.html")

        # Parser le HTML
        actual_result = parse_wigor_html(html_content)

        # Charger le résultat attendu
        expected_result = self.load_expected_result("expected_timetable.json")

        # Sauvegarder le résultat actuel pour débogage
        self.save_actual_result(actual_result, "expected_timetable.json")

        # Comparer les résultats
        if expected_result != actual_result:
            error_message = self.format_diff_message(expected_result, actual_result)
            self.fail(error_message)

        # Vérifications supplémentaires de structure
        self.assertIsInstance(actual_result, list, "Le résultat doit être une liste")

        for i, course in enumerate(actual_result):
            self.assertIsInstance(course, dict, f"Le cours à l'index {i} doit être un dictionnaire")

            # Vérifier la présence des champs critiques
            critical_fields = ["titre", "horaire"]
            for field in critical_fields:
                self.assertIn(
                    field, course, f"Le champ '{field}' est manquant dans le cours {i}: {course}"
                )

    def test_empty_html_parsing(self):
        """Test que le parser gère correctement le HTML vide."""
        empty_html = "<html><body></body></html>"
        result = parse_wigor_html(empty_html)

        self.assertIsInstance(result, list, "Le résultat doit être une liste même pour HTML vide")
        self.assertEqual(len(result), 0, "HTML vide devrait retourner une liste vide")

    def test_malformed_html_parsing(self):
        """Test que le parser gère les HTML malformés sans crash."""
        malformed_html = "<html><div>Contenu cassé<span>Non fermé</html>"

        # Ne doit pas lever d'exception
        try:
            result = parse_wigor_html(malformed_html)
            self.assertIsInstance(result, list, "Doit retourner une liste même avec HTML malformé")
        except Exception as e:
            self.fail(f"Le parser ne doit pas crash sur HTML malformé: {e}")

    def test_parser_output_structure(self):
        """Test de la structure générale de sortie du parser."""
        html_content = self.load_fixture("sample_timetable.html")
        result = parse_wigor_html(html_content)

        # Le résultat doit toujours être une liste
        self.assertIsInstance(result, list)

        # Chaque élément doit être un dictionnaire
        for i, item in enumerate(result):
            self.assertIsInstance(
                item, dict, f"L'élément {i} doit être un dictionnaire, reçu: {type(item)}"
            )


if __name__ == "__main__":
    # Configuration pour des messages d'erreur plus lisibles
    unittest.TestCase.maxDiff = None

    # Lancer les tests
    unittest.main(verbosity=2)
