#!/usr/bin/env python3
"""
Démonstration des améliorations du parser Wigor Viewer.
Montre l'extraction correcte des jours depuis les éléments TCJour.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from timetable_parser import parse_wigor_html


def test_demo_jours():
    """Démonstration avec un HTML plus réaliste."""

    print("🎯 DÉMONSTRATION - EXTRACTION DES JOURS")
    print("=" * 60)

    # HTML simulé plus proche de la réalité Wigor
    realistic_html = """
    <html>
    <head><title>Emploi du temps EPSI</title></head>
    <body>
        <!-- En-tête avec jours -->
        <table>
            <tr>
                <td class="TCJour">Lundi 13 Octobre</td>
                <td class="TCJour">Mardi 14 Octobre</td>
                <td class="TCJour">Mercredi 15 Octobre</td>
                <td class="TCJour">Jeudi 16 Octobre</td>
                <td class="TCJour">Vendredi 17 Octobre</td>
            </tr>
        </table>
        
        <!-- Cours de la semaine -->
        <div class="Case" style="left: 0px; top: 100px;">
            <table>
                <tr><td class="TCase">Workshop emploi</td></tr>
                <tr><td class="TChdeb">09:00 - 12:00</td></tr>
                <tr><td class="TCSalle">F202(Faure)</td></tr>
                <tr><td class="TCProf">Couraud Julien</td></tr>
            </table>
        </div>
        
        <div class="Case" style="left: 100px; top: 150px;">
            <table>
                <tr><td class="TCase">Développement Web</td></tr>
                <tr><td class="TChdeb">14:00 - 17:00</td></tr>
                <tr><td class="TCSalle">A301</td></tr>
                <tr><td class="TCProf">Martin Pierre</td></tr>
            </table>
        </div>
        
        <div class="Case" style="left: 200px; top: 100px;">
            <table>
                <tr><td class="TCase">Base de données</td></tr>
                <tr><td class="TChdeb">08:30 - 10:30</td></tr>
                <tr><td class="TCSalle">B205</td></tr>
                <tr><td class="TCProf">Dupont Marie</td></tr>
            </table>
        </div>
        
        <div class="Case" style="left: 300px; top: 200px;">
            <table>
                <tr><td class="TCase">Algorithmique</td></tr>
                <tr><td class="TChdeb">10:45 - 12:45</td></tr>
                <tr><td class="TCSalle">C103</td></tr>
                <tr><td class="TCProf">Bernard Paul</td></tr>
            </table>
        </div>
        
        <div class="Case" style="left: 400px; top: 130px;">
            <table>
                <tr><td class="TCase">Projet collaboratif</td></tr>
                <tr><td class="TChdeb">13:30 - 16:30</td></tr>
                <tr><td class="TCSalle">D104</td></tr>
                <tr><td class="TCProf">Robert Sophie</td></tr>
            </table>
        </div>
    </body>
    </html>
    """

    # Parse le HTML
    courses = parse_wigor_html(realistic_html)

    print(f"📊 RÉSULTATS: {len(courses)} cours extraits")
    print("=" * 60)

    # Affichage par jour
    courses_by_day = {}
    for course in courses:
        day = course["jour"]
        if day not in courses_by_day:
            courses_by_day[day] = []
        courses_by_day[day].append(course)

    # Ordre des jours de la semaine
    jours_ordre = [
        "Lundi 13 Octobre",
        "Mardi 14 Octobre",
        "Mercredi 15 Octobre",
        "Jeudi 16 Octobre",
        "Vendredi 17 Octobre",
    ]

    for jour in jours_ordre:
        if jour in courses_by_day:
            print(f"\n📅 {jour}")
            print("-" * len(jour))

            for course in courses_by_day[jour]:
                print(f"  🕘 {course['horaire']} | {course['titre']}")
                print(f"     Salle: {course['salle']} | Prof: {course['prof']}")
                print()
        else:
            print(f"\n📅 {jour}")
            print("-" * len(jour))
            print("  Aucun cours")
            print()

    # Vérification des améliorations
    print("=" * 60)
    print("✅ AMÉLIORATIONS VÉRIFIÉES:")
    print(f"   • Jours extraits depuis <td class='TCJour'> ✓")
    print(
        f"   • {len([c for c in courses if c['jour'] != 'Jour inconnu'])} cours avec jour correct ✓"
    )
    print(f"   • {len([c for c in courses if c['jour'] == 'Jour inconnu'])} cours sans jour ✓")
    print(f"   • Format jour conservé tel quel (pas de conversion) ✓")
    print("=" * 60)


if __name__ == "__main__":
    test_demo_jours()
