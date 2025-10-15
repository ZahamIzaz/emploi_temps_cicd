"""
Module pour l'authentification via cookies Wigor.
Contient les fonctions pour construire une session authentifiée et vérifier l'authentification.
"""

import logging
import re
from typing import Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuration du logger
logger = logging.getLogger(__name__)


def build_session_from_cookie_header(cookie_header: str) -> requests.Session:
    """
    Construit une session requests authentifiée à partir d'un header cookie.

    Args:
        cookie_header (str): Header cookie brut copié depuis l'onglet Network
                           Format: "ASP.NET_SessionId=value; .DotNetCasClientAuth=value; ..."

    Returns:
        requests.Session: Session configurée avec les cookies et headers appropriés

    Raises:
        ValueError: Si les cookies essentiels ne sont pas trouvés
    """
    if not cookie_header:
        raise ValueError("Le header cookie ne peut pas être vide")

    # Créer la session
    session = requests.Session()

    # Configuration des headers pour imiter Chrome
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
    )

    # Parser les cookies depuis le header
    cookies = _parse_cookie_header(cookie_header)

    # Vérifier la présence des cookies essentiels
    required_cookies = ["ASP.NET_SessionId", ".DotNetCasClientAuth"]
    missing_cookies = [cookie for cookie in required_cookies if cookie not in cookies]

    if missing_cookies:
        logger.warning(f"Cookies essentiels manquants: {missing_cookies}")
        # Ne pas lever d'exception, certains cookies peuvent être optionnels selon le contexte

    # Ajouter les cookies à la session
    for name, value in cookies.items():
        session.cookies.set(name, value)

    # Configuration de retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    logger.info(f"Session créée avec {len(cookies)} cookies")
    logger.debug(f"Cookies configurés: {list(cookies.keys())}")

    return session


def _parse_cookie_header(cookie_header: str) -> Dict[str, str]:
    """
    Parse un header cookie brut en dictionnaire.

    Args:
        cookie_header (str): Header cookie au format "name=value; name2=value2"

    Returns:
        Dict[str, str]: Dictionnaire des cookies {nom: valeur}
    """
    cookies = {}

    try:
        # Nettoyer le header (supprimer "Cookie: " si présent)
        clean_header = re.sub(r"^Cookie:\s*", "", cookie_header.strip(), flags=re.IGNORECASE)

        # Séparer les cookies par ";" et nettoyer les espaces
        cookie_pairs = [pair.strip() for pair in clean_header.split(";") if pair.strip()]

        for pair in cookie_pairs:
            if "=" in pair:
                # Séparer nom et valeur (seulement le premier "=")
                name, value = pair.split("=", 1)
                name = name.strip()
                value = value.strip()

                # Supprimer les guillemets si présents
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]

                cookies[name] = value
                logger.debug(
                    f"Cookie parsé: {name} = {value[:20]}{'...' if len(value) > 20 else ''}"
                )

    except Exception as e:
        logger.error(f"Erreur lors du parsing des cookies: {e}")
        raise ValueError(f"Format de cookie invalide: {e}")

    return cookies


def is_authenticated(session: requests.Session, url: str) -> bool:
    """
    Vérifie si la session est authentifiée en testant l'accès à une URL EDT.

    Args:
        session (requests.Session): Session à tester
        url (str): URL de la page EDT à tester

    Returns:
        bool: True si authentifié, False sinon
    """
    if not url:
        logger.error("URL de test vide")
        return False

    try:
        logger.info(f"Test d'authentification sur: {url}")

        # Faire une requête GET (stream=False pour gestion automatique du gzip)
        response = session.get(url, stream=False, timeout=30)

        # Vérifier le code de statut
        if response.status_code != 200:
            logger.warning(f"Code de statut inattendu: {response.status_code}")
            return False

        # Vérifier le contenu de la réponse
        content = response.text.lower()

        # Chercher les indicateurs d'une page EDT authentifiée
        auth_indicators = ["edt -", "innercase", "emploi du temps", "tcase", "tchdeb"]

        for indicator in auth_indicators:
            if indicator in content:
                logger.info(f"Authentification confirmée (indicateur trouvé: '{indicator}')")
                return True

        # Vérifier s'il s'agit d'une page de connexion
        login_indicators = ["login", "connexion", "authentification", "sign in", "password"]
        for indicator in login_indicators:
            if indicator in content:
                logger.warning(f"Page de connexion détectée (indicateur: '{indicator}')")
                return False

        logger.warning("Aucun indicateur d'authentification trouvé dans la réponse")
        logger.debug(f"Début de la réponse: {response.text[:500]}")
        return False

    except requests.exceptions.Timeout:
        logger.error("Timeout lors du test d'authentification")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de requête lors du test d'authentification: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors du test d'authentification: {e}")
        return False


def validate_session_cookies(session: requests.Session) -> Dict[str, bool]:
    """
    Valide la présence des cookies essentiels dans la session.

    Args:
        session (requests.Session): Session à valider

    Returns:
        Dict[str, bool]: État de validation de chaque cookie essentiel
    """
    required_cookies = {"ASP.NET_SessionId": False, ".DotNetCasClientAuth": False}

    for cookie in session.cookies:
        if cookie.name in required_cookies:
            required_cookies[cookie.name] = True

    return required_cookies


def refresh_session_if_needed(session: requests.Session, test_url: str) -> bool:
    """
    Teste et rafraîchit la session si nécessaire.

    Args:
        session (requests.Session): Session à tester
        test_url (str): URL pour tester l'authentification

    Returns:
        bool: True si la session est valide, False sinon
    """
    if is_authenticated(session, test_url):
        logger.info("Session toujours valide")
        return True
    else:
        logger.warning("Session expirée ou invalide")
        return False


# Configuration du logging pour ce module
def setup_logging(level: str = "INFO"):
    """
    Configure le système de logging pour le module cookies_auth.

    Args:
        level (str): Niveau de logging (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
