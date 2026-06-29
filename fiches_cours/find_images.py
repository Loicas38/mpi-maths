#!/usr/bin/env python3
"""
Script de démonstration du support des images
Recherche les cartes Anki contenant des images
"""
import requests
import json
import re

def invoke_anki(action, **params):
    """Invoque une action AnkiConnect"""
    response = requests.post('http://localhost:8765', json={
        'action': action,
        'version': 6,
        'params': params
    })
    return response.json()

def find_cards_with_images(deck_pattern="prépa::MP2I::Maths"):
    """Recherche les cartes contenant des images"""
    print(f"🔍 Recherche de cartes avec images dans '{deck_pattern}'...\n")
    
    # Récupérer les cartes du paquet
    result = invoke_anki('findCards', query=f'deck:"{deck_pattern}"')
    
    if result.get('error'):
        print(f"✗ Erreur: {result['error']}")
        return
    
    card_ids = result.get('result', [])
    print(f"📊 {len(card_ids)} carte(s) trouvée(s) dans le paquet")
    
    # Récupérer les infos des cartes
    result = invoke_anki('cardsInfo', cards=card_ids[:100])  # Limité aux 100 premières
    cards_info = result.get('result', [])
    
    # Chercher les cartes avec images
    cards_with_images = []
    
    for card in cards_info:
        note_id = card.get('note')
        
        # Récupérer les champs de la note
        note_result = invoke_anki('notesInfo', notes=[note_id])
        note_info = note_result.get('result', [{}])[0]
        
        fields = note_info.get('fields', {})
        
        # Vérifier si un champ contient une balise <img>
        has_image = False
        image_field = None
        image_src = None
        
        for field_name, field_data in fields.items():
            field_value = field_data.get('value', '')
            if '<img' in field_value.lower():
                has_image = True
                image_field = field_name
                
                # Extraire le nom de l'image
                match = re.search(r'src=["\']([^"\']+)["\']', field_value, re.IGNORECASE)
                if match:
                    image_src = match.group(1)
                break
        
        if has_image:
            cards_with_images.append({
                'card_id': card.get('cardId'),
                'note_id': note_id,
                'deck': card.get('deckName'),
                'model': note_info.get('modelName'),
                'field': image_field,
                'image': image_src,
                'tags': note_info.get('tags', [])
            })
    
    print(f"\n📷 {len(cards_with_images)} carte(s) avec image(s) trouvée(s):\n")
    
    for i, card in enumerate(cards_with_images[:10], 1):
        print(f"{i}. {card['deck']}")
        print(f"   Type: {card['model']}")
        print(f"   Champ: {card['field']}")
        print(f"   Image: {card['image']}")
        print(f"   Tags: {', '.join(card['tags']) if card['tags'] else 'aucun'}")
        print()
    
    if len(cards_with_images) > 10:
        print(f"... et {len(cards_with_images) - 10} autre(s)")

if __name__ == "__main__":
    print("=== Recherche de cartes avec images ===\n")
    
    # Tester la connexion
    result = invoke_anki('version')
    if result.get('error'):
        print(f"✗ Impossible de se connecter à Anki: {result['error']}")
    else:
        print(f"✓ Connecté à AnkiConnect version {result['result']}\n")
        find_cards_with_images()
