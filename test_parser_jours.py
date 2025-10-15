#!/usr/bin/env python3
"""
Test rapide du parser amélioré pour vérifier l'extraction des jours.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from timetable_parser import parse_wigor_html
import logging

# Configuration des logs pour voir le détail
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

# HTML de test avec la structure TCJour
test_html = '''
<html>
<body>
    <!-- Jours de la semaine -->
    <td class="TCJour">Lundi 13 Octobre</td>
    <td class="TCJour">Mardi 14 Octobre</td>
    <td class="TCJour">Mercredi 15 Octobre</td>
    <td class="TCJour">Jeudi 16 Octobre</td>
    <td class="TCJour">Vendredi 17 Octobre</td>
    
    <!-- Cours exemple -->
    <div class="Case" style="left: 0px;">
        <td class="TCase">Workshop</td>
        <td class="TChdeb">09:00 - 12:00</td>
        <td class="TCSalle">F202(Faure)</td>
        <td class="TCProf">Couraud Julien</td>
    </div>
    
    <div class="Case" style="left: 100px;">
        <td class="TCase">Développement</td>
        <td class="TChdeb">14:00 - 17:00</td>
        <td class="TCSalle">A301</td>
        <td class="TCProf">Martin Pierre</td>
    </div>
</body>
</html>
'''

print("🧪 TEST DU PARSER AMÉLIORÉ")
print("=" * 40)

# Test du parsing
courses = parse_wigor_html(test_html)

print(f"\n📊 RÉSULTATS: {len(courses)} cours trouvés")
print("=" * 40)

for i, course in enumerate(courses, 1):
    print(f"\n📅 COURS {i}:")
    print(f"  Jour: {course['jour']}")
    print(f"  Horaire: {course['horaire']}")
    print(f"  Cours: {course['titre']}")
    print(f"  Professeur: {course['prof']}")
    print(f"  Salle: {course['salle']}")

print("\n" + "=" * 40)
print("✅ Test terminé!")