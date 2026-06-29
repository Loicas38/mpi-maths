#!/usr/bin/env python3
"""
Script de test pour vérifier le support des images
"""
import requests
import json

def test_anki_connection():
    """Test la connexion à AnkiConnect"""
    try:
        response = requests.post('http://localhost:8765', json={
            'action': 'version',
            'version': 6
        })
        result = response.json()
        print(f"✓ Connexion à Anki réussie. Version AnkiConnect: {result['result']}")
        return True
    except Exception as e:
        print(f"✗ Erreur de connexion à Anki: {e}")
        return False

def test_retrieve_media():
    """Test la récupération d'un fichier média"""
    # Liste d'abord tous les médias disponibles
    try:
        response = requests.post('http://localhost:8765', json={
            'action': 'getMediaFilesNames',
            'version': 6,
            'params': {
                'pattern': '*'
            }
        })
        result = response.json()
        
        if result.get('error'):
            print(f"✗ Erreur lors de la récupération de la liste des médias: {result['error']}")
            return
        
        media_files = result.get('result', [])
        print(f"\n📁 {len(media_files)} fichier(s) média trouvé(s) dans Anki")
        
        # Afficher les 10 premiers
        if media_files:
            print("\nExemples de fichiers média:")
            for i, filename in enumerate(media_files[:10]):
                print(f"  {i+1}. {filename}")
            
            # Tester la récupération du premier fichier image
            image_files = [f for f in media_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg'))]
            if image_files:
                test_file = image_files[0]
                print(f"\n🧪 Test de récupération de: {test_file}")
                
                response = requests.post('http://localhost:8765', json={
                    'action': 'retrieveMediaFile',
                    'version': 6,
                    'params': {
                        'filename': test_file
                    }
                })
                result = response.json()
                
                if result.get('error'):
                    print(f"✗ Erreur: {result['error']}")
                elif result.get('result'):
                    print(f"✓ Image récupérée avec succès ({len(result['result'])} caractères en base64)")
                else:
                    print(f"✗ Aucun résultat retourné")
            else:
                print("\n⚠ Aucun fichier image trouvé")
        else:
            print("⚠ Aucun fichier média trouvé dans Anki")
            
    except Exception as e:
        print(f"✗ Erreur: {e}")

if __name__ == "__main__":
    print("=== Test du support des images Anki ===\n")
    if test_anki_connection():
        test_retrieve_media()
