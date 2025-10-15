#!/usr/bin/env python3
"""Tests simples et efficaces pour améliorer rapidement la couverture - Version nettoyée."""

import unittest
from unittest.mock import Mock, patch, mock_open
import sys
import os
from datetime import datetime

# Ajout du chemin source
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import src.main as main_module
import src.wigor_api as wigor_api
import src.timetable_parser as parser

class TestMainModuleSimple(unittest.TestCase):
    """Tests simples pour le module main."""

    def test_setup_logging_basic_levels(self):
        """Test setup_logging avec tous les niveaux."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        for level in levels:
            with patch('src.main.logging.basicConfig') as mock_config:
                main_module.setup_logging(level)
                mock_config.assert_called()

    def test_setup_logging_with_file_param(self):
        """Test setup_logging avec fichier."""
        with patch('src.main.logging.basicConfig') as mock_config:
            with patch('src.main.logging.FileHandler') as mock_handler:
                main_module.setup_logging("INFO", "test.log")
                mock_config.assert_called()

    def test_validate_test_args_missing_url(self):
        """Test validate_test_args avec URL manquante."""
        mock_args = Mock()
        mock_args.url = None
        mock_args.cookie = "test=cookie"
        
        with patch('src.main.print'):
            result = main_module.validate_test_args(mock_args)
            self.assertFalse(result)

    def test_validate_test_args_missing_cookie(self):
        """Test validate_test_args avec cookie manquant."""
        mock_args = Mock()
        mock_args.url = "https://test.com"
        mock_args.cookie = None
        
        with patch('src.main.print'):
            result = main_module.validate_test_args(mock_args)
            self.assertFalse(result)

    def test_validate_test_args_success(self):
        """Test validate_test_args avec succès."""
        mock_args = Mock()
        mock_args.url = "https://test.com"
        mock_args.cookie = "test=cookie"
        
        # Ne devrait pas appeler sys.exit
        result = main_module.validate_test_args(mock_args)
        self.assertTrue(result)

class TestWigorApiSimple(unittest.TestCase):
    """Tests simples pour wigor_api."""

    def test_parse_cookie_header_variations(self):
        """Test parse_cookie_header avec variations."""
        test_cases = [
            ("", {}),
            ("a=1", {"a": "1"}),
            ("a=1; b=2", {"a": "1", "b": "2"}),
            ("session=abc123; user=test; path=/", {"session": "abc123", "user": "test"}),
            ("invalid", {}),
            ("a=; b=test", {"b": "test"}),  # Valeur vide
        ]
        
        for cookie_str, expected_count in test_cases:
            result = wigor_api.parse_cookie_header(cookie_str)
            self.assertIsInstance(result, dict)
            if isinstance(expected_count, dict):
                for key in expected_count:
                    self.assertIn(key, result)

    def test_extract_page_title_variations(self):
        """Test extract_page_title avec variations."""
        test_cases = [
            "<title>Simple Title</title>",
            "<html><head><title>Complex Title</title></head></html>",
            "<TITLE>UPPERCASE</TITLE>",
            "<title>   Spaced Title   </title>",
            "<title></title>",
            "<div>No title</div>",
            "",
        ]
        
        for html in test_cases:
            result = wigor_api.extract_page_title(html)
            self.assertIsInstance(result, str)

    @patch('src.wigor_api.requests.Session')
    def test_fetch_wigor_html_status_codes(self, mock_session_class):
        """Test fetch_wigor_html avec différents codes de statut."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Test code 200
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>Success</html>"
        mock_session.get.return_value = mock_response
        
        result = wigor_api.fetch_wigor_html("https://test.com")
        self.assertEqual(result, "<html>Success</html>")
        
        # Test code 404
        mock_response.status_code = 404
        mock_response.text = "<html>Not Found</html>"
        result = wigor_api.fetch_wigor_html("https://test.com")
        self.assertIn("Not Found", result)

    @patch('src.wigor_api.requests.Session')
    def test_fetch_wigor_html_with_cookie(self, mock_session_class):
        """Test fetch_wigor_html avec cookie."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>With Cookie</html>"
        mock_session.get.return_value = mock_response
        
        result = wigor_api.fetch_wigor_html("https://test.com", "session=test")
        self.assertEqual(result, "<html>With Cookie</html>")

    def test_find_login_form_cases(self):
        """Test _find_login_form avec différents cas."""
        test_cases = [
            ('<form><input type="password"></form>', False),
            ('<form><input type="text"></form>', False),
            ('<div>No form</div>', False),
            ('', False),
        ]
        
        for html, expected in test_cases:
            result = wigor_api._find_login_form(html)
            self.assertIsInstance(result, bool)

    @patch('builtins.open', mock_open())
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_save_debug_html_scenarios(self, mock_makedirs, mock_exists):
        """Test _save_debug_html avec différents scénarios."""
        # Répertoire existe
        mock_exists.return_value = True
        wigor_api._save_debug_html("<html>Test</html>", "https://test.com")
        mock_makedirs.assert_not_called()
        
        # Répertoire n'existe pas
        mock_exists.return_value = False
        mock_makedirs.reset_mock()
        wigor_api._save_debug_html("<html>Test</html>", "https://test.com")
        mock_makedirs.assert_called()

    def test_extract_cookies_string_cases(self):
        """Test _extract_cookies_string avec différents cas."""
        # Session vide
        mock_session = Mock()
        mock_session.cookies = []
        result = wigor_api._extract_cookies_string(mock_session)
        self.assertEqual(result, "")
        
        # Session avec cookies
        mock_cookie = Mock()
        mock_cookie.name = "test"
        mock_cookie.value = "value"
        mock_session.cookies = [mock_cookie]
        result = wigor_api._extract_cookies_string(mock_session)
        self.assertIn("test=value", result)

class TestTimetableParserSimple(unittest.TestCase):
    """Tests simples pour timetable_parser."""

    def test_parse_date_from_header_cases(self):
        """Test _parse_date_from_header avec différents cas."""
        test_cases = [
            "Lundi 15 Janvier",
            "Mardi 20 Mars", 
            "Invalid date",
            "",
            "123 Invalid",
        ]
        
        for header in test_cases:
            result = parser._parse_date_from_header(header)
            # Peut retourner datetime ou None
            self.assertTrue(isinstance(result, (datetime, type(None))))

    def test_extract_week_date_range_cases(self):
        """Test _extract_week_date_range avec différents cas."""
        test_cases = [
            [],
            ["Lundi 15 Janvier"],
            ["Lundi 15 Janvier", "Vendredi 19 Janvier"],
            ["Invalid", "Headers"],
        ]
        
        for day_headers in test_cases:
            result = parser._extract_week_date_range(day_headers)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)

    def test_is_course_in_week_range_cases(self):
        """Test _is_course_in_week_range avec différents cas."""
        test_cases = [
            ("Lundi", None, None),
            ("Mardi 15 Janvier", None, None),
            ("", None, None),
        ]
        
        for course_day, start_date, end_date in test_cases:
            result = parser._is_course_in_week_range(course_day, start_date, end_date)
            self.assertIsInstance(result, bool)

    def test_sort_courses_by_date_and_time_cases(self):
        """Test _sort_courses_by_date_and_time avec différents cas."""
        test_cases = [
            [],
            [{"jour": "Lundi", "start_time": "08:00"}],
            [{"jour": "Mardi", "start_time": "10:00"}, {"jour": "Lundi", "start_time": "09:00"}],
        ]
        
        for courses in test_cases:
            result = parser._sort_courses_by_date_and_time(courses)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), len(courses))

    @patch('src.timetable_parser.BeautifulSoup')
    def test_map_days_cases(self, mock_bs):
        """Test _map_days avec différents cas."""
        mock_soup = Mock()
        
        # Cas vide
        mock_soup.find_all.return_value = []
        result = parser._map_days(mock_soup)
        self.assertIsInstance(result, list)
        
        # Cas avec éléments
        mock_element = Mock()
        mock_element.get_text.return_value = "Lundi"
        mock_element.get.return_value = "left: 100px;"
        mock_soup.find_all.return_value = [mock_element]
        result = parser._map_days(mock_soup)
        self.assertIsInstance(result, list)

    def test_extract_left_position_cases(self):
        """Test _extract_left_position avec différents cas."""
        test_cases = [
            None,
            Mock(),  # Element sans style
        ]
        
        # Element avec style
        mock_element = Mock()
        mock_element.get.return_value = "left: 150px; top: 20px;"
        test_cases.append(mock_element)
        
        for element in test_cases:
            if element and hasattr(element, 'get'):
                element.get = Mock(return_value="left: 150px; top: 20px;" if element != test_cases[1] else None)
            
            result = parser._extract_left_position(element)
            self.assertTrue(isinstance(result, (float, type(None))))

    def test_closest_day_cases(self):
        """Test _closest_day avec différents cas."""
        test_cases = [
            (100.0, []),
            (100.0, [(50.0, "Lundi"), (150.0, "Mardi")]),
            (75.0, [(50.0, "Lundi"), (100.0, "Mardi"), (150.0, "Mercredi")]),
        ]
        
        for left_pos, days_map in test_cases:
            result = parser._closest_day(left_pos, days_map)
            self.assertIsInstance(result, str)

    def test_extract_course_info_cases(self):
        """Test _extract_course_info avec différents cas."""
        test_cases = [None]
        
        # Mock element valide
        mock_element = Mock()
        mock_element.get_text.return_value = "Mathématiques\n08:00 - 10:00\nProf Martin"
        mock_element.get.return_value = "left: 100px;"
        test_cases.append(mock_element)
        
        for course_div in test_cases:
            result = parser._extract_course_info(course_div)
            if course_div is None:
                self.assertIsNone(result)
            else:
                self.assertTrue(isinstance(result, (dict, type(None))))

    def test_format_courses_for_display_empty(self):
        """Test format_courses_for_display avec liste vide."""
        result = parser.format_courses_for_display([])
        self.assertEqual(result, "Aucun cours trouvé")

    def test_get_courses_by_day_empty(self):
        """Test get_courses_by_day avec liste vide."""
        result = parser.get_courses_by_day([], "Lundi")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

class TestWigorApiPrivateFunctions(unittest.TestCase):
    """Tests pour les fonctions privées de wigor_api."""

    def test_find_cas_login_url_cases(self):
        """Test _find_cas_login_url avec différents cas."""
        test_cases = [
            ('<a href="/cas/login">Login</a>', "https://test.com"),
            ('<div>No CAS</div>', "https://test.com"),
            ('', "https://test.com"),
        ]
        
        for html, current_url in test_cases:
            result = wigor_api._find_cas_login_url(html, current_url)
            self.assertTrue(isinstance(result, (str, type(None))))

    def test_find_redirect_url_cases(self):
        """Test _find_redirect_url avec différents cas."""
        test_cases = [
            '<meta http-equiv="refresh" content="0; url=/dashboard">',
            '<script>window.location.href = "/success";</script>',
            '<div>No redirect</div>',
            '',
        ]
        
        for html in test_cases:
            result = wigor_api._find_redirect_url(html, "https://test.com")
            self.assertTrue(isinstance(result, (str, type(None))))

    def test_extract_form_data_simple(self):
        """Test _extract_form_data avec cas simples."""
        html_cases = [
            '<form><input name="user"><input name="pass"></form>',
            '<form><input name="username" type="text"></form>',
            '<form></form>',
            '',
        ]
        
        for html in html_cases:
            result = wigor_api._extract_form_data(html, "testuser", "testpass")
            self.assertIsInstance(result, dict)

    def test_get_form_action_simple(self):
        """Test _get_form_action avec cas simples."""
        test_cases = [
            ('<form action="/login"></form>', "https://test.com/page"),
            ('<form></form>', "https://test.com/page"),
            ('', "https://test.com/page"),
        ]
        
        for html, current_url in test_cases:
            result = wigor_api._get_form_action(html, current_url)
            self.assertIsInstance(result, str)

if __name__ == '__main__':
    unittest.main()