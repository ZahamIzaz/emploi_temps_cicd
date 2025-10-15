"""
Tests unitaires pour les fonctions de timetable_parser.py et wigor_api.py
"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

# Ajouter le chemin du module parent pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.timetable_parser import parse_wigor_html, _map_days, _extract_left_position, _closest_day, _extract_course_info
from src.wigor_api import fetch_wigor_html, parse_cookie_header


class TestTimetableParser(unittest.TestCase):
    """Tests pour le parser d'emploi du temps Wigor."""
    
    def setUp(self):
        """Prépare les données de test."""
        # HTML simulé basé sur le format Wigor réel
        self.sample_html = """
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <title>EDT - Emploi du temps</title>
        </head>
        <body>
            <div class="Jour">
                <table>
                    <tr>
                        <td class="TCJour" style="left: 120px;">Lundi 14 Octobre</td>
                        <td class="TCJour" style="left: 240px;">Mardi 15 Octobre</td>
                        <td class="TCJour" style="left: 360px;">Mercredi 16 Octobre</td>
                    </tr>
                </table>
            </div>
            
            <div class="Case" style="left: 125px; top: 100px;">
                <table>
                    <tr>
                        <td class="TCase">Mathématiques Avancées</td>
                    </tr>
                    <tr>
                        <td class="TChdeb">08:00 - 10:00</td>
                    </tr>
                    <tr>
                        <td class="TCSalle">Salle A101</td>
                    </tr>
                    <tr>
                        <td class="TCProf">M. Dupont - Groupe A</td>
                    </tr>
                </table>
            </div>
            
            <div class="Case" style="left: 245px; top: 150px;">
                <table>
                    <tr>
                        <td class="TCase">Programmation Python</td>
                    </tr>
                    <tr>
                        <td class="TChdeb">14:00 - 17:00</td>
                    </tr>
                    <tr>
                        <td class="TCSalle">Labo B205</td>
                    </tr>
                    <tr>
                        <td class="TCProf">Mme Martin - Groupe B</td>
                    </tr>
                </table>
            </div>
            
            <div class="Case" style="left: 365px; top: 200px;">
                <table>
                    <tr>
                        <td class="TCase">Base de Données</td>
                    </tr>
                    <tr>
                        <td class="TChdeb">09:30 - 12:30</td>
                    </tr>
                    <tr>
                        <td class="TCSalle">C302</td>
                    </tr>
                    <tr>
                        <td class="TCProf">Dr. Bernard</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        # HTML minimal pour tests d'erreur
        self.empty_html = "<html><body></body></html>"
        
        # HTML avec cours incomplet
        self.incomplete_html = """
        <html>
        <body>
            <div class="Case" style="left: 125px;">
                <table>
                    <tr>
                        <td class="TCase">Cours Sans Détails</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
    
    def test_parse_wigor_html_basic(self):
        """Test basique : vérifier qu'on détecte au moins 1 cours."""
        courses = parse_wigor_html(self.sample_html)
        
        # Vérifier qu'on a trouvé des cours
        self.assertGreater(len(courses), 0, "Aucun cours détecté")
        self.assertEqual(len(courses), 3, "Nombre de cours incorrect")
    
    def test_parse_wigor_html_course_details(self):
        """Test détaillé : vérifier les informations des cours."""
        courses = parse_wigor_html(self.sample_html)
        
        # Trier les cours par jour pour avoir un ordre prévisible
        courses_by_title = {course['titre']: course for course in courses}
        
        # Test du premier cours (Mathématiques)
        math_course = courses_by_title.get('Mathématiques Avancées')
        self.assertIsNotNone(math_course, "Cours de Mathématiques non trouvé")
        self.assertEqual(math_course['titre'], 'Mathématiques Avancées')
        self.assertEqual(math_course['horaire'], '08:00 - 10:00')
        self.assertEqual(math_course['salle'], 'Salle A101')
        self.assertEqual(math_course['prof'], 'M. Dupont - Groupe A')
        self.assertEqual(math_course['jour'], 'Lundi 14 Octobre')
        
        # Test du deuxième cours (Python)
        python_course = courses_by_title.get('Programmation Python')
        self.assertIsNotNone(python_course, "Cours de Python non trouvé")
        self.assertEqual(python_course['titre'], 'Programmation Python')
        self.assertEqual(python_course['horaire'], '14:00 - 17:00')
        self.assertEqual(python_course['salle'], 'Labo B205')
        self.assertEqual(python_course['prof'], 'Mme Martin - Groupe B')
        self.assertEqual(python_course['jour'], 'Mardi 15 Octobre')
        
        # Test du troisième cours (BDD)
        bdd_course = courses_by_title.get('Base de Données')
        self.assertIsNotNone(bdd_course, "Cours de BDD non trouvé")
        self.assertEqual(bdd_course['titre'], 'Base de Données')
        self.assertEqual(bdd_course['horaire'], '09:30 - 12:30')
        self.assertEqual(bdd_course['salle'], 'C302')
        self.assertEqual(bdd_course['prof'], 'Dr. Bernard')
        self.assertEqual(bdd_course['jour'], 'Mercredi 16 Octobre')
    
    def test_parse_wigor_html_empty(self):
        """Test avec HTML vide."""
        courses = parse_wigor_html(self.empty_html)
        self.assertEqual(len(courses), 0, "Des cours ont été trouvés dans un HTML vide")
    
    def test_parse_wigor_html_none(self):
        """Test avec HTML None ou vide."""
        courses = parse_wigor_html("")
        self.assertEqual(len(courses), 0, "Des cours ont été trouvés avec HTML vide")
        
        courses = parse_wigor_html(None)
        self.assertEqual(len(courses), 0, "Des cours ont été trouvés avec HTML None")
    
    def test_map_days_function(self):
        """Test de la fonction _map_days."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(self.sample_html, 'html.parser')
        days = _map_days(soup)
        
        # Vérifier qu'on a trouvé 3 jours
        self.assertEqual(len(days), 3, "Nombre de jours incorrect")
        
        # Vérifier l'ordre (trié par position left)
        self.assertEqual(days[0][1], 'Lundi 14 Octobre')
        self.assertEqual(days[1][1], 'Mardi 15 Octobre')
        self.assertEqual(days[2][1], 'Mercredi 16 Octobre')
        
        # Vérifier les positions
        self.assertEqual(days[0][0], 120.0)
        self.assertEqual(days[1][0], 240.0)
        self.assertEqual(days[2][0], 360.0)
    
    def test_extract_left_position(self):
        """Test de l'extraction de position left."""
        from bs4 import BeautifulSoup
        
        # Test avec pixels
        html = '<div style="left: 125px; top: 100px;"></div>'
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div')
        
        position = _extract_left_position(div)
        self.assertEqual(position, 125.0)
        
        # Test avec pourcentage
        html = '<div style="left: 50%;"></div>'
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div')
        
        position = _extract_left_position(div)
        self.assertEqual(position, 50.0)
        
        # Test sans style
        html = '<div></div>'
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div')
        
        position = _extract_left_position(div)
        self.assertIsNone(position)
    
    def test_closest_day(self):
        """Test de la fonction _closest_day."""
        days_map = [(120.0, 'Lundi'), (240.0, 'Mardi'), (360.0, 'Mercredi')]
        
        # Test position proche du lundi
        self.assertEqual(_closest_day(125.0, days_map), 'Lundi')
        
        # Test position proche du mardi
        self.assertEqual(_closest_day(245.0, days_map), 'Mardi')
        
        # Test position exacte
        self.assertEqual(_closest_day(360.0, days_map), 'Mercredi')
        
        # Test avec liste vide
        self.assertEqual(_closest_day(125.0, []), 'Jour inconnu')
    
    def test_extract_course_info(self):
        """Test de l'extraction d'informations de cours."""
        from bs4 import BeautifulSoup
        
        html = """
        <div class="Case">
            <table>
                <tr><td class="TCase">Test Cours</td></tr>
                <tr><td class="TChdeb">10:00 - 12:00</td></tr>
                <tr><td class="TCSalle">A100</td></tr>
                <tr><td class="TCProf">Prof Test</td></tr>
            </table>
        </div>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div')
        
        course_info = _extract_course_info(div)
        
        self.assertIsNotNone(course_info)
        self.assertEqual(course_info['titre'], 'Test Cours')
        self.assertEqual(course_info['horaire'], '10:00 - 12:00')
        self.assertEqual(course_info['salle'], 'A100')
        self.assertEqual(course_info['prof'], 'Prof Test')


class TestWigorAPI(unittest.TestCase):
    """Tests pour l'API Wigor."""
    
    def test_parse_cookie_header(self):
        """Test du parsing des cookies."""
        # Test cookie simple
        cookie_str = "ASP.NET_SessionId=abc123; .DotNetCasClientAuth=xyz789"
        cookies = parse_cookie_header(cookie_str)
        
        self.assertEqual(len(cookies), 2)
        self.assertEqual(cookies['ASP.NET_SessionId'], 'abc123')
        self.assertEqual(cookies['.DotNetCasClientAuth'], 'xyz789')
        
        # Test cookie avec espaces
        cookie_str = " ASP.NET_SessionId = abc123 ; .DotNetCasClientAuth = xyz789 "
        cookies = parse_cookie_header(cookie_str)
        
        self.assertEqual(len(cookies), 2)
        self.assertEqual(cookies['ASP.NET_SessionId'], 'abc123')
        
        # Test cookie vide
        cookies = parse_cookie_header("")
        self.assertEqual(len(cookies), 0)
    
    @patch('src.wigor_api.requests.Session.get')
    def test_fetch_wigor_html_success(self, mock_get):
        """Test du téléchargement HTML avec mock."""
        # Configurer le mock
        mock_response = Mock()
        mock_response.text = self.get_sample_html_response()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()  # Ne lève pas d'exception
        mock_get.return_value = mock_response
        
        # Tester la fonction
        url = "https://wigor.epsi.fr/test"
        cookie = "ASP.NET_SessionId=test123"
        
        html = fetch_wigor_html(url, cookie)
        
        # Vérifications
        self.assertIsNotNone(html)
        self.assertIn("EDT - Test", html)
        mock_get.assert_called_once()
        mock_response.raise_for_status.assert_called_once()
    
    @patch('src.wigor_api.requests.Session.get')
    def test_fetch_wigor_html_with_session(self, mock_get):
        """Test du téléchargement HTML avec session fournie."""
        from unittest.mock import Mock
        import requests
        
        # Configurer le mock
        mock_response = Mock()
        mock_response.text = "<html><title>Test Session</title></html>"
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        
        # Créer une session mock
        mock_session = Mock(spec=requests.Session)
        mock_session.get.return_value = mock_response
        
        # Tester la fonction
        url = "https://wigor.epsi.fr/test"
        html = fetch_wigor_html(url, session=mock_session)
        
        # Vérifications
        self.assertIsNotNone(html)
        self.assertIn("Test Session", html)
        mock_session.get.assert_called_once_with(url, allow_redirects=True)
    
    @patch('src.wigor_api.requests.Session.get')
    def test_fetch_wigor_html_error(self, mock_get):
        """Test de gestion d'erreur lors du téléchargement."""
        import requests
        
        # Configurer le mock pour lever une exception
        mock_get.side_effect = requests.exceptions.RequestException("Erreur de connexion")
        
        # Tester que l'exception est bien propagée
        url = "https://wigor.epsi.fr/test"
        cookie = "ASP.NET_SessionId=test123"
        
        with self.assertRaises(requests.exceptions.RequestException):
            fetch_wigor_html(url, cookie)
    
    def test_fetch_wigor_html_invalid_url(self):
        """Test avec URL invalide."""
        with self.assertRaises(ValueError):
            fetch_wigor_html("", "cookie=test")
    
    def get_sample_html_response(self):
        """Retourne un exemple de réponse HTML."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>EDT - Test</title>
        </head>
        <body>
            <div class="Case" style="left: 125px;">
                <table>
                    <tr><td class="TCase">Cours Test</td></tr>
                    <tr><td class="TChdeb">08:00 - 10:00</td></tr>
                    <tr><td class="TCSalle">A101</td></tr>
                    <tr><td class="TCProf">Prof Test</td></tr>
                </table>
            </div>
        </body>
        </html>
        """


class TestIntegration(unittest.TestCase):
    """Tests d'intégration combinant parser et API."""
    
    @patch('src.wigor_api.requests.Session.get')
    def test_full_workflow(self, mock_get):
        """Test du workflow complet : téléchargement + parsing."""
        # HTML avec plusieurs cours
        sample_html = """
        <html>
        <head><title>EDT - Integration Test</title></head>
        <body>
            <div class="Jour">
                <table>
                    <tr>
                        <td class="TCJour" style="left: 120px;">Lundi 14 Oct</td>
                    </tr>
                </table>
            </div>
            <div class="Case" style="left: 125px;">
                <table>
                    <tr><td class="TCase">Intégration</td></tr>
                    <tr><td class="TChdeb">09:00 - 11:00</td></tr>
                    <tr><td class="TCSalle">B301</td></tr>
                    <tr><td class="TCProf">M. Test</td></tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        # Configurer le mock
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Workflow complet
        html = fetch_wigor_html("https://test.com", "cookie=test")
        courses = parse_wigor_html(html)
        
        # Vérifications
        self.assertEqual(len(courses), 1)
        course = courses[0]
        self.assertEqual(course['titre'], 'Intégration')
        self.assertEqual(course['horaire'], '09:00 - 11:00')
        self.assertEqual(course['salle'], 'B301')
        self.assertEqual(course['prof'], 'M. Test')
        self.assertEqual(course['jour'], 'Lundi 14 Oct')


if __name__ == '__main__':
    # Configuration du logging pour les tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Lancer les tests
    unittest.main(verbosity=2)
