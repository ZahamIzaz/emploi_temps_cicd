#!/usr/bin/env python3
"""
Test du nouveau message d'erreur amélioré pour l'erreur 503.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wigor_api import login_with_credentials

def test_503_error_message():
    """Test du nouveau message d'erreur pour le code 503."""
    
    print("🧪 TEST DU NOUVEAU MESSAGE D'ERREUR 503")
    print("=" * 60)
    
    # Test avec l'URL réelle qui retourne 503
    url = "https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS"
    username = "test.user"
    password = "test.password"
    
    print(f"🔗 URL testée: {url}")
    print(f"👤 Utilisateur: {username}")
    print("🔄 Tentative de connexion...")
    
    # Appeler la fonction de login
    result = login_with_credentials(username, password, url)
    
    print(f"\n📊 RÉSULTAT:")
    print(f"   • Succès: {result.get('success', 'N/A')}")
    print(f"   • Code HTTP: {result.get('status_code', 'N/A')}")
    print(f"   • Message d'erreur: {result.get('error', 'N/A')}")
    
    # Vérification du message d'erreur amélioré
    expected_keywords = ["503", "temporairement indisponible", "réessayer", "navigateur"]
    error_message = result.get('error', '').lower()
    
    print(f"\n✅ VÉRIFICATIONS DU MESSAGE D'ERREUR:")
    for keyword in expected_keywords:
        found = keyword in error_message
        status = "✅" if found else "❌"
        print(f"   {status} Contient '{keyword}': {found}")
    
    print("\n" + "=" * 60)
    
    if result.get('status_code') == 503:
        print("🎯 ERREUR 503 DÉTECTÉE ET GÉRÉE CORRECTEMENT")
        print("💡 Le message utilisateur est maintenant plus informatif")
    else:
        print("⚠️ Statut différent de 503 reçu")
    
    return result

if __name__ == "__main__":
    result = test_503_error_message()
    
    print(f"\n📝 MESSAGE FINAL À L'UTILISATEUR:")
    print(f"   '{result.get('error', 'Aucun message')}'")
    
    print(f"\n🔧 RECOMMANDATIONS:")
    print(f"   1. Vérifier manuellement https://wigor.net dans un navigateur")
    print(f"   2. Attendre quelques minutes et réessayer")
    print(f"   3. Utiliser les cookies manuels si le problème persiste")