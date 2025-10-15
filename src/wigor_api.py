"""
Module pour interagir avec l'API Wigor.
Contient les fonctions pour l'authentification et la récupération des données d'emploi du temps.
"""

import logging
import re
from typing import Dict, Optional, Union, List
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from urllib.parse import urljoin, urlparse
try:
    from .timetable_parser import parse_wigor_html
except ImportError:
    from src.timetable_parser import parse_wigor_html

# Configuration du logger
logger = logging.getLogger(__name__)


def parse_cookie_header(cookie_header: str) -> Dict[str, str]:
    """
    Convertit un header cookie au format "k=v; k2=v2" en dictionnaire.
    
    Args:
        cookie_header (str): Header cookie au format "k=v; k2=v2"
        
    Returns:
        Dict[str, str]: Dictionnaire des cookies {nom: valeur}
    """
    cookies = {}
    if cookie_header:
        # Séparer les cookies par ";" et nettoyer les espaces
        cookie_pairs = [pair.strip() for pair in cookie_header.split(';')]
        for pair in cookie_pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                cookies[key.strip()] = value.strip()
    return cookies


def fetch_wigor_html(url: str, cookie_header: str = "", session: Optional[requests.Session] = None) -> str:
    """
    Télécharge la page de l'emploi du temps Wigor.
    
    Args:
        url (str): URL de la page Wigor à télécharger
        cookie_header (str): Header cookie au format "k=v; k2=v2" (ignoré si session fournie)
        session (Optional[requests.Session]): Session existante à réutiliser
        
    Returns:
        str: Contenu HTML de la page
        
    Raises:
        requests.RequestException: En cas d'erreur lors de la requête
        ValueError: En cas d'URL invalide
    """
    if not url:
        raise ValueError("L'URL ne peut pas être vide")
    
    # Utiliser la session fournie ou en créer une nouvelle
    if session is not None:
        # Réutiliser exactement la session fournie
        current_session = session
        logger.debug("Utilisation de la session fournie")
    else:
        # Créer une nouvelle session avec cookies
        cookies = parse_cookie_header(cookie_header)
        current_session = requests.Session()
        current_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        })
        # Ajouter les cookies à la session
        for name, value in cookies.items():
            current_session.cookies.set(name, value)
        logger.debug(f"Nouvelle session créée avec cookies: {list(cookies.keys())}")
    
    try:
        logger.info(f"Requête vers: {url}")
        
        # Effectuer la requête GET avec allow_redirects=True et conservation des headers
        response = current_session.get(url, allow_redirects=True)
        response.raise_for_status()  # Lever une exception si erreur HTTP
        
        # Extraction du titre de la page pour le logging
        title = extract_page_title(response.text)
        
        # Vérifier si la page contient 'innerCase'
        contains_inner_case = 'innerCase' in response.text.lower()
        
        # Logging des informations de la réponse
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Taille du HTML: {len(response.text)} caractères")
        logger.info(f"Response URL: {response.url}")
        logger.info(f"Titre de la page: {title}")
        logger.info(f"Contient innerCase: {contains_inner_case}")
        
        # Sauvegarder le contenu dans un fichier de debug
        _save_debug_html(response.text, response.url)
        
        return response.text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la requête vers {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        raise


def extract_page_title(html_content: str) -> Optional[str]:
    """
    Extrait le titre d'une page HTML.
    
    Args:
        html_content (str): Contenu HTML de la page
        
    Returns:
        Optional[str]: Titre de la page ou None si non trouvé
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        return "Titre non trouvé"
    except Exception as e:
        logger.warning(f"Erreur lors de l'extraction du titre: {e}")
        return "Erreur extraction titre"


def get_wigor_timetable(url: str, cookie_header: str = "", session: Optional[requests.Session] = None) -> Dict[str, Union[str, List[Dict[str, str]]]]:
    """
    Fonction principale pour récupérer et parser l'emploi du temps Wigor.
    
    Args:
        url (str): URL de la page Wigor
        cookie_header (str): Header cookie d'authentification (ignoré si session fournie)
        session (Optional[requests.Session]): Session existante à réutiliser
        
    Returns:
        Dict[str, Union[str, List[Dict[str, str]]]]: Dictionnaire contenant:
            - 'html': HTML brut de la page
            - 'courses': Liste des cours parsés
    """
    try:
        # Récupérer le HTML
        html_content = fetch_wigor_html(url, cookie_header, session)
        
        # Parser les cours
        parsed_courses = parse_wigor_html(html_content)
        
        logger.info(f"Emploi du temps récupéré avec succès: {len(parsed_courses)} cours trouvés")
        
        return {
            'html': html_content,
            'courses': parsed_courses
        }
        
    except Exception as e:
        logger.error(f"Échec de récupération de l'emploi du temps: {e}")
        raise


def get_wigor_timetable_legacy(url: str, cookie_header: str) -> str:
    """
    Version legacy pour compatibilité - retourne seulement le HTML.
    
    Args:
        url (str): URL de la page Wigor
        cookie_header (str): Header cookie d'authentification
        
    Returns:
        str: HTML de l'emploi du temps
        
    Deprecated:
        Utilisez get_wigor_timetable() qui retourne HTML + cours parsés
    """
    try:
        return fetch_wigor_html(url, cookie_header)
    except Exception as e:
        logger.error(f"Échec de récupération de l'emploi du temps: {e}")
        raise


def _save_debug_html(html_content: str, response_url: str):
    """
    Sauvegarde le contenu HTML dans un fichier de debug.
    
    Args:
        html_content (str): Contenu HTML à sauvegarder
        response_url (str): URL de la réponse
    """
    try:
        # Créer le dossier _debug s'il n'existe pas
        debug_dir = "_debug"
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
            logger.info(f"Dossier de debug créé: {debug_dir}")
        
        # Générer le nom de fichier avec la date
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"edt_{timestamp}.html"
        filepath = os.path.join(debug_dir, filename)
        
        # Sauvegarder le fichier
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"<!-- URL: {response_url} -->\n")
            f.write(f"<!-- Timestamp: {datetime.now().isoformat()} -->\n")
            f.write(f"<!-- Size: {len(html_content)} characters -->\n")
            f.write(html_content)
        
        logger.info(f"HTML sauvegardé dans: {filepath}")
        
    except Exception as e:
        logger.warning(f"Erreur lors de la sauvegarde debug: {e}")


def login_with_credentials(username: str, password: str, url: str) -> Dict[str, Union[bool, str, requests.Session, int]]:
    """
    Se connecte à Wigor avec identifiant et mot de passe.
    
    Args:
        username (str): Identifiant utilisateur
        password (str): Mot de passe
        url (str): URL Wigor de base
        
    Returns:
        Dict contenant:
            - success (bool): True si connexion réussie
            - session (requests.Session): Session authentifiée si succès
            - cookies_string (str): Cookies au format string si succès
            - error (str): Message d'erreur si échec
            - status_code (int): Code HTTP de la dernière réponse
    """
    logger.info(f"Tentative de connexion pour l'utilisateur: {username}")
    
    # Créer une session avec headers réalistes
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    })
    
    try:
        # Étape 1: GET initial sur l'URL Wigor pour déclencher la redirection
        logger.info("Étape 1: Accès à la page Wigor pour déclencher la redirection")
        response = session.get(url, allow_redirects=True)
        
        logger.info(f"Réponse initiale - Status: {response.status_code}, URL: {response.url}")
        
        # Gestion spécifique des erreurs serveur
        if response.status_code == 503:
            return {
                'success': False,
                'error': 'Service Wigor temporairement indisponible (503). Veuillez réessayer dans quelques minutes ou vérifiez si le site fonctionne dans votre navigateur.',
                'status_code': response.status_code
            }
        elif response.status_code >= 500:
            return {
                'success': False,
                'error': f'Erreur serveur Wigor ({response.status_code}). Le service pourrait être en maintenance.',
                'status_code': response.status_code
            }
        elif response.status_code >= 400:
            return {
                'success': False,
                'error': f'Erreur d\'accès ({response.status_code}). Vérifiez l\'URL ou réessayez plus tard.',
                'status_code': response.status_code
            }
        
        # Vérifier si on est déjà sur une page de login ou si on a besoin de redirection
        login_form = _find_login_form(response.text)
        
        if not login_form:
            # Chercher un lien de connexion ou forcer une redirection
            logger.info("Aucun formulaire de login trouvé, recherche de redirection CAS")
            cas_url = _find_cas_login_url(response.text, response.url)
            
            if cas_url:
                logger.info(f"URL CAS trouvée: {cas_url}")
                response = session.get(cas_url, allow_redirects=True)
                login_form = _find_login_form(response.text)
            else:
                return {
                    'success': False,
                    'error': 'Impossible de trouver la page de connexion CAS',
                    'status_code': response.status_code
                }
        
        if not login_form:
            return {
                'success': False,
                'error': 'Formulaire de connexion non trouvé',
                'status_code': response.status_code
            }
        
        # Étape 2: Extraire les champs du formulaire et préparer le POST
        logger.info("Étape 2: Extraction des champs du formulaire de connexion")
        form_data = _extract_form_data(response.text, username, password)
        form_action = _get_form_action(response.text, response.url)
        
        logger.info(f"Action du formulaire: {form_action}")
        logger.info(f"Champs du formulaire: {list(form_data.keys())}")
        
        # Étape 3: Soumettre les identifiants
        logger.info("Étape 3: Soumission des identifiants")
        session.headers.update({
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': f"{urlparse(response.url).scheme}://{urlparse(response.url).netloc}",
            'Referer': response.url
        })
        
        response = session.post(form_action, data=form_data, allow_redirects=True)
        logger.info(f"Réponse POST - Status: {response.status_code}, URL: {response.url}")
        
        # Étape 4: Suivre les redirections jusqu'au domaine wigorservices.net
        logger.info("Étape 4: Suivi des redirections vers wigorservices.net")
        max_redirects = 10
        redirect_count = 0
        
        while redirect_count < max_redirects:
            if 'wigorservices.net' in response.url or 'wigor.epsi.fr' in response.url:
                logger.info(f"Arrivé sur le domaine Wigor: {response.url}")
                break
            
            # Chercher des redirections JavaScript ou meta refresh
            next_url = _find_redirect_url(response.text, response.url)
            if next_url:
                logger.info(f"Redirection détectée vers: {next_url}")
                response = session.get(next_url, allow_redirects=True)
                redirect_count += 1
            else:
                break
        
        # Étape 5: Vérifier que la connexion a réussi
        logger.info("Étape 5: Vérification de la connexion")
        success_indicators = ['EDT -', 'innerCase', 'emploi du temps', 'edt']
        content_lower = response.text.lower()
        
        is_authenticated = any(indicator.lower() in content_lower for indicator in success_indicators)
        
        if is_authenticated:
            logger.info("Connexion réussie - indicateurs trouvés")
            
            # Extraire les cookies de la session
            cookies_string = _extract_cookies_string(session)
            
            # Sauvegarder le HTML de debug
            _save_debug_html(response.text, response.url)
            
            return {
                'success': True,
                'session': session,
                'cookies_string': cookies_string,
                'status_code': response.status_code
            }
        else:
            logger.warning("Connexion échouée - indicateurs non trouvés")
            
            # Vérifier si c'est une erreur d'authentification
            error_indicators = ['invalid', 'incorrect', 'erreur', 'échec', 'failed']
            if any(indicator in content_lower for indicator in error_indicators):
                error_msg = "Identifiants incorrects"
            else:
                error_msg = "Impossible de vérifier la connexion"
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': response.status_code
            }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de requête lors de la connexion: {e}")
        return {
            'success': False,
            'error': f"Erreur de réseau: {str(e)}",
            'status_code': 0
        }
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la connexion: {e}")
        return {
            'success': False,
            'error': f"Erreur inattendue: {str(e)}",
            'status_code': 0
        }


def _find_login_form(html_content: str) -> bool:
    """
    Cherche un formulaire de connexion dans le HTML.
    
    Args:
        html_content (str): Contenu HTML à analyser
        
    Returns:
        bool: True si un formulaire de login est trouvé
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Chercher des formulaires contenant des champs username/password
    forms = soup.find_all('form')
    for form in forms:
        inputs = form.find_all('input')
        input_names = [input.get('name', '').lower() for input in inputs]
        
        has_username = any('username' in name or 'login' in name or 'user' in name for name in input_names)
        has_password = any('password' in name or 'pwd' in name for name in input_names)
        
        if has_username and has_password:
            return True
    
    return False


def _find_cas_login_url(html_content: str, current_url: str) -> Optional[str]:
    """
    Cherche une URL de connexion CAS dans le HTML.
    
    Args:
        html_content (str): Contenu HTML
        current_url (str): URL actuelle
        
    Returns:
        Optional[str]: URL CAS ou None
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Chercher des liens vers CAS
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href', '')
        if 'cas' in href.lower() or 'login' in href.lower() or 'connexion' in href.lower():
            return urljoin(current_url, href)
    
    # Chercher des redirections JavaScript
    scripts = soup.find_all('script')
    for script in scripts:
        script_text = script.get_text()
        if 'location.href' in script_text or 'window.location' in script_text:
            # Extraire l'URL avec regex simple
            url_match = re.search(r'["\']([^"\']*cas[^"\']*)["\']', script_text)
            if url_match:
                return urljoin(current_url, url_match.group(1))
    
    return None


def _extract_form_data(html_content: str, username: str, password: str) -> Dict[str, str]:
    """
    Extrait les données du formulaire de connexion.
    
    Args:
        html_content (str): HTML contenant le formulaire
        username (str): Nom d'utilisateur
        password (str): Mot de passe
        
    Returns:
        Dict[str, str]: Données du formulaire
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    form_data = {}
    
    # Trouver le formulaire de login
    forms = soup.find_all('form')
    login_form = None
    
    for form in forms:
        inputs = form.find_all('input')
        input_names = [input.get('name', '').lower() for input in inputs]
        
        has_username = any('username' in name or 'login' in name or 'user' in name for name in input_names)
        has_password = any('password' in name or 'pwd' in name for name in input_names)
        
        if has_username and has_password:
            login_form = form
            break
    
    if not login_form:
        return form_data
    
    # Extraire tous les champs du formulaire
    inputs = login_form.find_all('input')
    
    for input_field in inputs:
        name = input_field.get('name', '')
        value = input_field.get('value', '')
        input_type = input_field.get('type', '').lower()
        
        if name:
            if 'username' in name.lower() or 'login' in name.lower() or 'user' in name.lower():
                form_data[name] = username
            elif 'password' in name.lower() or 'pwd' in name.lower():
                form_data[name] = password
            elif input_type == 'hidden':
                # Inclure tous les champs cachés (lt, execution, _eventId, etc.)
                form_data[name] = value
                logger.debug(f"Champ caché ajouté: {name} = {value}")
            elif input_type in ['text', 'email']:
                # Autres champs texte (peut être username avec un autre nom)
                if not form_data.get(name):  # Seulement si pas déjà rempli
                    form_data[name] = username if 'mail' not in name.lower() else username
    
    # Champs spéciaux CAS souvent requis
    if 'execution' not in form_data:
        execution_input = soup.find('input', {'name': 'execution'})
        if execution_input:
            form_data['execution'] = execution_input.get('value', '')
    
    if 'lt' not in form_data:
        lt_input = soup.find('input', {'name': 'lt'})
        if lt_input:
            form_data['lt'] = lt_input.get('value', '')
    
    if '_eventId' not in form_data:
        form_data['_eventId'] = 'submit'
    
    return form_data


def _get_form_action(html_content: str, current_url: str) -> str:
    """
    Extrait l'action du formulaire de connexion.
    
    Args:
        html_content (str): HTML contenant le formulaire
        current_url (str): URL actuelle pour résolution relative
        
    Returns:
        str: URL d'action du formulaire
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Trouver le formulaire de login
    forms = soup.find_all('form')
    for form in forms:
        inputs = form.find_all('input')
        input_names = [input.get('name', '').lower() for input in inputs]
        
        has_username = any('username' in name or 'login' in name or 'user' in name for name in input_names)
        has_password = any('password' in name or 'pwd' in name for name in input_names)
        
        if has_username and has_password:
            action = form.get('action', '')
            if action:
                return urljoin(current_url, action)
            else:
                return current_url
    
    return current_url


def _find_redirect_url(html_content: str, current_url: str) -> Optional[str]:
    """
    Cherche une URL de redirection dans le HTML.
    
    Args:
        html_content (str): Contenu HTML
        current_url (str): URL actuelle
        
    Returns:
        Optional[str]: URL de redirection ou None
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Chercher meta refresh
    meta_refresh = soup.find('meta', {'http-equiv': 'refresh'})
    if meta_refresh:
        content = meta_refresh.get('content', '')
        url_match = re.search(r'url=(.+)', content, re.IGNORECASE)
        if url_match:
            return urljoin(current_url, url_match.group(1).strip())
    
    # Chercher redirection JavaScript
    scripts = soup.find_all('script')
    for script in scripts:
        script_text = script.get_text()
        
        # location.href = "url"
        href_match = re.search(r'location\.href\s*=\s*["\']([^"\']+)["\']', script_text)
        if href_match:
            return urljoin(current_url, href_match.group(1))
        
        # window.location = "url"
        location_match = re.search(r'window\.location\s*=\s*["\']([^"\']+)["\']', script_text)
        if location_match:
            return urljoin(current_url, location_match.group(1))
    
    return None


def _extract_cookies_string(session: requests.Session) -> str:
    """
    Extrait les cookies de la session au format string.
    
    Args:
        session (requests.Session): Session authentifiée
        
    Returns:
        str: Cookies au format "name=value; name2=value2"
    """
    cookie_pairs = []
    
    for cookie in session.cookies:
        cookie_pairs.append(f"{cookie.name}={cookie.value}")
    
    cookies_string = "; ".join(cookie_pairs)
    logger.info(f"Cookies extraits: {len(session.cookies)} cookies")
    logger.debug(f"Cookies: {[cookie.name for cookie in session.cookies]}")
    
    return cookies_string


# Configuration du logging pour ce module
def setup_logging(level: str = "INFO"):
    """
    Configure le système de logging pour le module wigor_api.
    
    Args:
        level (str): Niveau de logging (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
