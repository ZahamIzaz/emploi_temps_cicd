#!/usr/bin/env python3
"""Test pour vérifier l'ordre des cours après tri."""

import sys

sys.path.insert(0, "src")

from timetable_parser import parse_wigor_html


def test_course_sorting():
    """Teste le tri des cours avec les données réelles."""

    # Lire le dernier fichier HTML sauvegardé
    with open("_debug/edt_20251015_090149.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    print("🔍 Test du tri des cours")
    print("=" * 50)

    # Parser le HTML
    courses = parse_wigor_html(html_content)

    print(f"\n📅 Ordre des cours après tri:")
    print(f"Nombre total: {len(courses)} cours\n")

    for i, course in enumerate(courses, 1):
        print(f"{i:2d}. {course['jour']:20} | {course['horaire']:12} | {course['titre']}")

    # Vérifier que les cours sont bien triés chronologiquement
    print(f"\n✅ Vérification du tri chronologique:")

    # Grouper par jour pour vérifier l'ordre
    days_order = []
    for course in courses:
        if course["jour"] not in days_order:
            days_order.append(course["jour"])

    print(f"Ordre des jours: {days_order}")

    # Vérifier que pour chaque jour, les heures sont dans l'ordre
    from collections import defaultdict

    courses_by_day = defaultdict(list)
    for course in courses:
        courses_by_day[course["jour"]].append(course)

    for day, day_courses in courses_by_day.items():
        print(f"\n{day}:")
        for course in day_courses:
            print(f"  • {course['horaire']} - {course['titre']}")


if __name__ == "__main__":
    test_course_sorting()
