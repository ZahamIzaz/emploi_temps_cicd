"""
Module pour parser les données HTML de Wigor et extraire l'emploi du temps.
Transforme le HTML brut en liste structurée de cours.
"""

import logging
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Configuration du logger
logger = logging.getLogger(__name__)

# Mapping des mois français vers leur numéro
MONTH_NAMES = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}


def _parse_date_from_header(header: str) -> Optional[datetime]:
    """
    Parse une date depuis un en-tête de jour (ex: "Lundi 13 Octobre").
    
    Args:
        header (str): En-tête du jour (ex: "Lundi 13 Octobre")
        
    Returns:
        Optional[datetime]: Date parsée ou None si échec
    """
    try:
        # Nettoyer et normaliser le header
        header = header.strip().lower()
        
        # Patterns possibles: "Lundi 13 Octobre", "Lundi 13 Oct", "13 Octobre", etc.
        # Extraire le jour et le mois
        match = re.search(r'(\d{1,2})\s+([a-zéèêàâôûç]+)', header)
        if not match:
            logger.debug(f"Impossible d'extraire jour/mois de: '{header}'")
            return None
            
        day = int(match.group(1))
        month_str = match.group(2).lower()
        
        # Trouver le mois correspondant
        month = None
        for french_month, month_num in MONTH_NAMES.items():
            if month_str.startswith(french_month[:3]):  # Match avec les 3 premières lettres
                month = month_num
                break
        
        if month is None:
            logger.debug(f"Mois non reconnu: '{month_str}' dans '{header}'")
            return None
        
        # Utiliser l'année courante par défaut
        current_year = datetime.now().year
        
        # Créer la date
        date = datetime(current_year, month, day)
        logger.debug(f"Date parsée: {header} -> {date.strftime('%Y-%m-%d')}")
        return date
        
    except Exception as e:
        logger.debug(f"Erreur parsing date '{header}': {e}")
        return None


def _extract_week_date_range(day_headers: List[str]) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Extrait la plage de dates de la semaine principale à partir des en-têtes de jours.
    Filtre les dates parasites d'autres semaines en ne gardant que les 5-7 premiers jours consécutifs.
    
    Args:
        day_headers (List[str]): Liste des en-têtes de jours
        
    Returns:
        Tuple[Optional[datetime], Optional[datetime]]: (date_debut, date_fin) ou (None, None)
    """
    parsed_dates = []
    
    # Parser toutes les dates valides
    for header in day_headers:
        date = _parse_date_from_header(header)
        if date:
            parsed_dates.append((date, header))
    
    if not parsed_dates:
        logger.warning("Aucune date valide trouvée dans les en-têtes")
        return None, None
    
    # Trier les dates par ordre chronologique
    parsed_dates.sort(key=lambda x: x[0])
    
    # Identifier la semaine principale (séquence la plus longue de jours consécutifs)
    main_week_dates = []
    current_sequence = [parsed_dates[0]]
    
    for i in range(1, len(parsed_dates)):
        prev_date = parsed_dates[i-1][0]
        curr_date = parsed_dates[i][0]
        
        # Si la différence est de 1 jour, c'est dans la même séquence
        if (curr_date - prev_date).days == 1:
            current_sequence.append(parsed_dates[i])
        else:
            # Fin de séquence, commencer une nouvelle
            if len(current_sequence) > len(main_week_dates):
                main_week_dates = current_sequence
            current_sequence = [parsed_dates[i]]
    
    # Ne pas oublier la dernière séquence
    if len(current_sequence) > len(main_week_dates):
        main_week_dates = current_sequence
    
    if not main_week_dates:
        logger.warning("Aucune séquence de dates consécutives trouvée")
        return None, None
    
    # Limiter à max 7 jours (semaine complète)
    if len(main_week_dates) > 7:
        main_week_dates = main_week_dates[:7]
    
    start_date = main_week_dates[0][0]
    end_date = main_week_dates[-1][0]
    
    # Logguer les dates de la semaine principale identifiée
    main_week_headers = [item[1] for item in main_week_dates]
    logger.info(f"Semaine principale identifiée: {main_week_headers}")
    logger.info(f"Plage de dates de la semaine courante: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    
    return start_date, end_date


def _is_course_in_week_range(course_day_header: str, start_date: Optional[datetime], end_date: Optional[datetime]) -> bool:
    """
    Vérifie si un cours appartient à la plage de dates de la semaine courante.
    
    Args:
        course_day_header (str): En-tête du jour du cours
        start_date (Optional[datetime]): Date de début de la semaine
        end_date (Optional[datetime]): Date de fin de la semaine
        
    Returns:
        bool: True si le cours est dans la plage, False sinon
    """
    if start_date is None or end_date is None:
        # Si pas de plage détectée, accepter tous les cours
        return True
    
    course_date = _parse_date_from_header(course_day_header)
    if course_date is None:
        # Si impossible de parser la date du cours, l'accepter par défaut
        logger.debug(f"Date non parsable pour cours: '{course_day_header}', accepté par défaut")
        return True
    
    # Vérifier si la date du cours est dans la plage
    is_in_range = start_date <= course_date <= end_date
    if not is_in_range:
        logger.debug(f"Cours filtré - date {course_date.strftime('%Y-%m-%d')} hors plage {start_date.strftime('%Y-%m-%d')}-{end_date.strftime('%Y-%m-%d')}")
    
    return is_in_range


def _sort_courses_by_date_and_time(courses: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Trie les cours par date puis par heure de début.
    
    Args:
        courses (List[Dict[str, str]]): Liste des cours à trier
        
    Returns:
        List[Dict[str, str]]: Liste des cours triés
    """
    def get_sort_key(course: Dict[str, str]) -> Tuple[Optional[datetime], str]:
        """Génère une clé de tri pour un cours (date, heure_debut)."""
        # Parser la date du jour
        date = _parse_date_from_header(course.get("jour", ""))
        
        # Parser l'heure de début depuis l'horaire (format "08:00-12:00" ou "08:00 - 12:00")
        horaire = course.get("horaire", "")
        heure_debut = "00:00"  # Valeur par défaut
        
        # Extraire l'heure de début
        if horaire:
            # Chercher le pattern HH:MM au début
            time_match = re.search(r'^(\d{1,2}:\d{2})', horaire.strip())
            if time_match:
                heure_debut = time_match.group(1)
        
        return (date, heure_debut)
    
    try:
        # Trier les cours avec gestion des erreurs
        sorted_courses = sorted(courses, key=get_sort_key)
        logger.info(f"📅 Cours triés par date et heure: {len(sorted_courses)} cours")
        return sorted_courses
        
    except Exception as e:
        logger.warning(f"Erreur lors du tri des cours: {e}")
        # En cas d'erreur, retourner la liste non triée
        return courses


def parse_wigor_html(html: str) -> List[Dict[str, str]]:
    """
    Parse le HTML de l'emploi du temps Wigor et extrait les cours.
    
    Args:
        html (str): Code HTML de la page Wigor
        
    Returns:
        List[Dict[str, str]]: Liste des cours avec leurs informations
            Format: [{"jour": ..., "titre": ..., "prof": ..., "horaire": ..., "salle": ...}, ...]
    """
    if not html:
        logger.warning("HTML vide fourni au parser")
        return []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. Extraire uniquement les en-têtes de jours de la semaine principale visible
        # La semaine principale a des positions CSS left entre 100% et 200% environ
        day_headers = []
        
        # Chercher tous les div.Jour qui contiennent les en-têtes de jours
        day_divs = soup.select("div.Jour")
        logger.debug(f"Nombre de div.Jour trouvés: {len(day_divs)}")
        
        for day_div in day_divs:
            # Extraire la position left depuis le style
            style = day_div.get('style', '')
            left_match = re.search(r'left:([0-9.]+)%', style)
            
            if left_match:
                left_percent = float(left_match.group(1))
                
                # Ne garder que les jours de la semaine principale visible (left entre 100% et 200%)
                if 100 <= left_percent <= 200:
                    td_jour = day_div.select_one("td.TCJour")
                    if td_jour:
                        day_text = td_jour.get_text(strip=True)
                        if day_text:
                            day_headers.append(day_text)
                            logger.debug(f"Jour de la semaine principale: {day_text} (left: {left_percent}%)")
        
        # Fallback si aucun jour trouvé avec la méthode position CSS
        if not day_headers:
            logger.warning("Aucun jour trouvé avec les positions CSS, utilisation du fallback")
            all_day_cells = [td.get_text(strip=True) 
                            for td in soup.select("td.TCJour")]
            day_headers = list(dict.fromkeys(all_day_cells))
            
            # Limiter aux 7 premiers pour éviter les dates parasites
            if len(day_headers) > 7:
                day_headers = day_headers[:7]
        
        logger.info(f"En-têtes de jours bruts trouvés: {day_headers}")
        
        # 2. Analyser la plage de dates de la semaine courante
        start_date, end_date = _extract_week_date_range(day_headers)
        if start_date and end_date:
            logger.info(f"📅 Plage de dates détectée: {start_date.strftime('%A %d %B %Y')} → {end_date.strftime('%A %d %B %Y')}")
        else:
            logger.warning("⚠️ Impossible de déterminer la plage de dates, tous les cours seront conservés")
        
        # 3. Extraire tous les blocs de cours dans l'ordre d'apparition
        # Seulement les div.Case principaux, pas les div.innerCase qui sont à l'intérieur
        course_blocks = soup.select("div.Case")
        logger.info(f"Nombre de blocs de cours trouvés: {len(course_blocks)}")
        
        # Liste pour stocker tous les cours
        courses = []
        
        # Si aucun jour trouvé, utiliser fallback
        if not day_headers:
            logger.warning("Aucun en-tête de jour trouvé, utilisation du fallback")
            for course_block in course_blocks:
                course_info = _extract_course_info(course_block)
                if course_info:
                    course_info["jour"] = "Jour inconnu"
                    courses.append(course_info)
            return courses
        
        # 3. Créer un mapping des jours basé sur les positions géographiques
        days_map = _map_days(soup)
        logger.debug(f"Mapping des jours: {days_map}")
        
        # 4. Assigner les jours basé sur la position géographique (left) et filtrage par date  
        courses_before_filter = 0
        courses_filtered = 0
        
        for i, course_block in enumerate(course_blocks):
            try:
                # Extraire les informations du cours
                course_info = _extract_course_info(course_block)
                
                if course_info:
                    courses_before_filter += 1
                    
                    # Attribution basée sur la position géographique
                    left_position = _extract_left_position(course_block)
                    if left_position is not None and days_map:
                        day_name = _closest_day(left_position, days_map)
                    else:
                        # Fallback : attribution cyclique si position non trouvée
                        day_index = i % len(day_headers)
                        day_name = day_headers[day_index]
                        logger.debug(f"Fallback attribution cyclique pour cours {i+1}")
                    
                    course_info["jour"] = day_name
                    
                    # Filtrer par plage de dates de la semaine courante
                    if _is_course_in_week_range(day_name, start_date, end_date):
                        courses.append(course_info)
                        logger.debug(f"Cours {i+1}: {course_info['titre']} assigné à {day_name} (pos: {left_position}) ✅")
                    else:
                        courses_filtered += 1
                        logger.debug(f"Cours {i+1}: {course_info['titre']} filtré (hors période) ❌")
                
            except Exception as e:
                logger.warning(f"Erreur lors du parsing d'un cours: {e}")
                continue
        
        # 5. Trier les cours par date puis par heure
        courses_sorted = _sort_courses_by_date_and_time(courses)
        
        # 6. Afficher les statistiques de filtrage
        logger.info("📊 Statistiques de parsing:")
        logger.info(f"   • Cours trouvés avant filtrage: {courses_before_filter}")
        logger.info(f"   • Cours filtrés (hors période): {courses_filtered}")
        logger.info(f"   • Cours conservés (période courante): {len(courses_sorted)}")
        
        return courses_sorted
        
    except Exception as e:
        logger.error(f"Erreur lors du parsing HTML: {e}")
        return []


def _map_days(soup: BeautifulSoup) -> List[Tuple[float, str]]:
    """
    Extrait la liste des jours avec leurs positions left.
    
    Args:
        soup (BeautifulSoup): Objet BeautifulSoup du HTML
        
    Returns:
        List[Tuple[float, str]]: Liste de tuples (left, "Mardi 14 Octobre")
    """
    days = []
    
    try:
        # Méthode 1: Chercher d'abord les div.Jour qui contiennent les td.TCJour
        jour_divs = soup.select("div.Jour")
        logger.debug(f"Nombre de div.Jour trouvés: {len(jour_divs)}")
        
        for jour_div in jour_divs:
            # Chercher td.TCJour à l'intérieur du div.Jour
            td_jour = jour_div.find('td', class_='TCJour')
            if td_jour:
                day_text = td_jour.get_text(strip=True)
                if day_text:
                    # Extraire la position depuis le div.Jour parent (plus fiable)
                    left_position = _extract_left_position(jour_div)
                    if left_position is not None:
                        # Garder directement la position en pourcentage (plus fiable)
                        days.append((left_position, day_text))
                        logger.debug(f"Jour mappé: {day_text} à {left_position}%")
        
        # Méthode 2: Fallback - chercher directement les td.TCJour
        if not days:
            day_cells = soup.find_all('td', class_='TCJour')
            logger.debug(f"Fallback: Nombre d'éléments td.TCJour trouvés: {len(day_cells)}")
            
            for day_cell in day_cells:
                day_text = day_cell.get_text(strip=True)
                if not day_text:
                    continue
                
                left_position = _extract_left_position(day_cell)
                if left_position is not None:
                    days.append((left_position, day_text))
                    logger.debug(f"Jour mappé (fallback): {day_text} à la position {left_position}")
                else:
                    # Position factice basée sur l'index
                    column_index = len(days) * 200  # Espacement plus large
                    days.append((column_index, day_text))
                    logger.debug(f"Jour mappé sans position: {day_text} à {column_index}px (factice)")
        
        # Trier par position left
        days.sort(key=lambda x: x[0])
        logger.info(f"Mapping final des jours: {[(pos, jour) for pos, jour in days]}")
        
    except Exception as e:
        logger.error(f"Erreur lors du mapping des jours: {e}")
    
    return days


def _extract_left_position(element) -> Optional[float]:
    """
    Extrait la position left depuis l'attribut style d'un élément.
    
    Args:
        element: Élément BeautifulSoup
        
    Returns:
        Optional[float]: Position left en pixels ou None si non trouvée
    """
    try:
        style = element.get('style', '')
        if style:
            # Chercher left: XXXpx ou left:XXX%
            left_match = re.search(r'left\s*:\s*([0-9.]+)(?:px|%)?', style)
            if left_match:
                return float(left_match.group(1))
    except Exception as e:
        logger.debug(f"Erreur extraction position left: {e}")
    
    return None


def _closest_day(left_position: float, days_map: List[Tuple[float, str]]) -> str:
    """
    Trouve le jour le plus proche d'une position left donnée.
    
    Args:
        left_position (float): Position left à associer
        days_map (List[Tuple[float, str]]): Liste des jours mappés
        
    Returns:
        str: Nom du jour le plus proche
    """
    if not days_map:
        return "Jour inconnu"
    
    # Trouver le jour avec la distance minimale
    closest_day = min(days_map, key=lambda day: abs(day[0] - left_position))
    return closest_day[1]


def _extract_course_info(course_div) -> Optional[Dict[str, str]]:
    """
    Extrait les informations d'un cours depuis un div.Case.
    
    Args:
        course_div: Élément BeautifulSoup du cours
        
    Returns:
        Optional[Dict[str, str]]: Informations du cours ou None si erreur
    """
    try:
        course_info = {
            "titre": "",
            "prof": "",
            "horaire": "",
            "salle": ""
        }

        # Extraire le titre (td.TCase)
        title_elem = course_div.find('td', class_='TCase')
        if title_elem:
            course_info["titre"] = title_elem.get_text(strip=True)

        # Extraire l'horaire (td.TChdeb) - valeur brute, jamais extrapolée
        time_elem = course_div.find('td', class_='TChdeb')
        if time_elem:
            horaire_brut = time_elem.get_text(strip=True)
            # Correction : ne jamais extrapoler, prendre la valeur brute
            course_info["horaire"] = horaire_brut

        # Extraire la salle (td.TCSalle)
        room_elem = course_div.find('td', class_='TCSalle')
        if room_elem:
            course_info["salle"] = room_elem.get_text(strip=True)

        # Extraire prof + groupe (td.TCProf)
        prof_elem = course_div.find('td', class_='TCProf')
        if prof_elem:
            course_info["prof"] = prof_elem.get_text(strip=True)

        # Vérifier qu'au moins le titre est présent
        if course_info["titre"]:
            return course_info
        else:
            logger.warning("Cours sans titre trouvé, ignoré")
            return None

    except Exception as e:
        logger.warning(f"Erreur extraction info cours: {e}")
        return None


def format_courses_for_display(courses: List[Dict[str, str]]) -> str:
    """
    Formate la liste des cours pour l'affichage.
    
    Args:
        courses (List[Dict[str, str]]): Liste des cours
        
    Returns:
        str: Texte formaté pour l'affichage
    """
    if not courses:
        return "Aucun cours trouvé"
    
    # Grouper par jour
    courses_by_day = {}
    for course in courses:
        day = course["jour"]
        if day not in courses_by_day:
            courses_by_day[day] = []
        courses_by_day[day].append(course)
    
    # Formater l'affichage
    formatted_text = []
    for day, day_courses in courses_by_day.items():
        formatted_text.append(f"\n=== {day} ===")
        for course in day_courses:
            formatted_text.append(
                f"{course['horaire']} - {course['titre']}\n"
                f"  Salle: {course['salle']}\n"
                f"  Prof: {course['prof']}\n"
            )
    
    return "\n".join(formatted_text)


def get_courses_by_day(courses: List[Dict[str, str]], day_name: str) -> List[Dict[str, str]]:
    """
    Filtre les cours par jour.
    
    Args:
        courses (List[Dict[str, str]]): Liste complète des cours
        day_name (str): Nom du jour à filtrer
        
    Returns:
        List[Dict[str, str]]: Cours du jour spécifié
    """
    return [course for course in courses if day_name.lower() in course["jour"].lower()]
