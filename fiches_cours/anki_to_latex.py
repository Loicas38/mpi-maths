#!/usr/bin/env python3
"""
Script pour extraire les cartes Anki et les convertir en LaTeX
Utilise AnkiConnect pour accéder aux paquets Anki
"""

import json
import requests
import os
import hashlib
import re
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import subprocess


class AnkiConnector:
    """Classe pour interagir avec Anki via AnkiConnect"""
    
    def __init__(self, url='http://localhost:8765'):
        self.url = url
        
    def invoke(self, action, **params):
        """Envoie une requête à AnkiConnect"""
        request_json = json.dumps({
            'action': action,
            'version': 6,
            'params': params
        })
        
        try:
            response = requests.post(self.url, data=request_json)
            response.raise_for_status()
            result = response.json()
            
            if result.get('error'):
                raise Exception(f"Erreur AnkiConnect: {result['error']}")
            
            return result.get('result')
        except requests.exceptions.ConnectionError:
            raise Exception("Impossible de se connecter à Anki. Assurez-vous qu'Anki est ouvert et qu'AnkiConnect est installé.")
    
    def get_deck_names(self):
        """Récupère tous les noms de paquets"""
        return self.invoke('deckNames')
    
    def get_cards_from_deck(self, deck_name):
        """Récupère toutes les cartes d'un paquet"""
        query = f'"deck:{deck_name}"'
        card_ids = self.invoke('findCards', query=query)
        
        if not card_ids:
            return []
        
        cards_info = self.invoke('cardsInfo', cards=card_ids)
        return cards_info
    
    def get_note_info(self, note_id):
        """Récupère les informations d'une note"""
        notes = self.invoke('notesInfo', notes=[note_id])
        return notes[0] if notes else None
    
    """def get_child_decks(self, parent_deck):
        ""Récupère les sous-paquets directs d'un paquet parent""
        all_decks = self.get_deck_names()
        # Filtrer pour obtenir seulement les enfants directs (un seul niveau en dessous)
        pattern = re.escape(parent_deck) + r'::([^:]+)$'
        child_decks = []
        for deck in all_decks:
            match = re.match(pattern, deck)
            if match:
                child_decks.append(deck)
        return child_decks"""
    
    def get_cards_by_subdeck(self, deck_name):
        """Récupère toutes les cartes d'un paquet et de ses sous-paquets, sous forme de dictionnaire"""
        cards = self.get_cards_from_deck(deck_name)
        # les clés sont le nom des paquets, les valeurs les listes de cartes
        dico = {}

        # print(cards)
        for card in cards:
            if card['deckName'] in dico:
                dico[card['deckName']].append(card)
            else:
                dico[card['deckName']] = [card]

        return dico
    
    def get_child_decks(self, parent_deck):
        """Récupère les sous-paquets directs d'un paquet donné"""
        all_decks = self.get_deck_names()
        child_decks = [deck for deck in all_decks if deck.startswith(parent_deck + '::') and deck.count('::') == parent_deck.count('::') + 1]
        return child_decks
    
    def retrieve_media_file(self, filename):
        """Récupère un fichier média depuis Anki"""
        result = self.invoke('retrieveMediaFile', filename=filename)
        return result
    
    def store_media_file(self, filename, data):
        """Stocke un fichier média dans Anki"""
        return self.invoke('storeMediaFile', filename=filename, data=data)


class HTMLToLatexConverter:
    """Convertit du HTML et MathJax en LaTeX"""
    
    def __init__(self, anki_connector=None, images_dir=None):
        self.anki_connector = anki_connector
        self.images_dir = images_dir
        self.processed_images = set()
    
    def convert(self, html_content):
        """Convertit le contenu HTML/MathJax en LaTeX"""
        if not html_content:
            return ""
        
        text = html_content

        # Étape 0: Nettoyer les motifs de cloze Anki {{cx::contenu}}
        # Remplacer par le contenu uniquement (gère les retours à la ligne)
        text = re.sub(r'{{c\d+::(.*?)}}', r'\1', text, flags=re.DOTALL)
        
        # Étape 0.5: Supprimer les balises anki-mathjax en conservant le contenu
        text = re.sub(r'<anki-mathjax>(.*?)</anki-mathjax>', r'\1', text, flags=re.DOTALL | re.IGNORECASE)

        # Étape 1: Décoder les entités HTML
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        text = text.replace('&#x27;', "'")
        text = text.replace('#', "nb")
        text = text.replace('′', "'")
        text = text.replace('▶', r"\( \triangleright \)")

        list_of_subs = [
            ("𝑞", "q"),
            ("𝑝", "p"),
            ("𝑎", "a"),
            ("𝑏", "b"),
            ("𝑐", "c"),
            ("𝑥", "x"),
            ("𝑦", "y"),
            ("𝑧", "z"),
            ("𝑓", "f"),
            ("𝑔", "g"),
            ("𝑢", "u"),
            ("𝑣", "v"),
            ("𝑤", "w"),
            ("𝑠", "s"),
            ("𝑡", "t"),
            ("𝑟", "r"),
            ("𝑛", "n"),
            ("𝑚", "m"),
            ("𝑘", "k"),
            ("𝑙", "l"),
            ("𝑒", "e"),
            ("𝑖", "i"),
            ("𝑗", "j"),
            ("𝑂", "O"),
            ("𝑂(1)", r"O(1)"),
            ("𝑂(𝑛)", r"O(n)"),
            ("ℝ", r"\(\mathbb{R}\)"),
            ("ℕ", r"\(\mathbb{N}\)"),
            ("ℤ", r"\(\mathbb{Z}\)"),
            ("ℚ", r"\(\mathbb{Q}\)"),
            ("ℂ", r"\(\mathbb{C}\)"),
            ("∈", r"\(\in\)"),
            ("∉", r"\(\notin\)"),
            ("∪", r"\(\cup\)"),
            ("∩", r"\(\cap\)"),
            ("⊆", r"\(\subseteq\)"),
            ("⊇", r"\(\supseteq\)"),
            ("⊂", r"\(\subset\)"),
            ("⊃", r"\(\supset\)"),
            ("∀", r"\(\forall\)"),
            ("∃", r"\(\exists\)"),
            ("∄", r"\(\nexists\)"),
            ("∧", r"\(\wedge\)"),
            ("∨", r"\(\vee\)"),
            ("¬", r"\(\neg\)"),
            ("⇒", r"\(\Rightarrow\)"),
            ("⇔", r"\(\Leftrightarrow\)"),
            ("∑", r"\(\sum\)"),
            ("∏", r"\(\prod\)"),
            ("∫", r"\(\int\)"),
            ("∂", r"\(\partial\)"),
            ("∇", r"\(\nabla\)"),
            ("∈fty", r"\(\infty\)"),
            ("∝", r"\(\propto\)"),
            ("∠", r"\(\angle\)"),
            ("∥", r"\(\parallel\)"),
            ("∉", r"\(\notin\)"),
            ("∋", r"\(\ni\)"),
            ("∌", r"\(\not\ni\)"),
            ("∎", r"\(\blacksquare\)"),
            ("∴", r"\(\therefore\)"),
            ("∵", r"\(\because\)"),
            ("∶", r"\(:\)"),
            ("∷", r"\(::\)"),
            ("∸", r"\(\div\)"),
            ("∹", r"\(\cdot\)"),
            ("∺", r"\(\circ\)"),
            ("∻", r"\(\bullet\)"),
            ("∼", r"\(\sim\)"),
            ("≁", r"\(\nsim\)"),
            ("≂", r"\(\simeq\)"),
            ("≃", r"\(\approx\)"),
            ("≄", r"\(\nsimeq\)"),
            ("≅", r"\(\cong\)"),
            ("≆", r"\(\ncong\)"),
            ("≇", r"\(\asymp\)"),
            ("≈", r"\(\approx\)"),
            ("≉", r"\(\not\approx\)"),
            ("≊", r"\(\equiv\)"),
            ("≋", r"\(\not\equiv\)"),
            ("≌", r"\(\simeq\)"),
            ("≍", r"\(\sim\)"),
            ("≎", r"\(\cong\)"),
            ("≏", r"\(\ncong\)"),
            ("≐", r"\(\doteq\)"),
            ("≑", r"\(\doteqdot\)"),
            ("≒", r"\(\fallingdotseq\)"),
            ("≓", r"\(\risingdotseq\)"),
            ("≔", r"\(:=\)"),
            ("≕", r"\(=:\)"),
            ("≖", r"\(\eqcirc\)"),
            ("≗", r"\(\circeq\)"),
            ("≘", r"\(\triangleq\)"),
            ("≙", r"\(\bumpeq\)"),
            ("≚", r"\(\Bumpeq\)"),
            ("≛", r"\(\doteq\)"),
            ("≜", r"\(\coloneqq\)"),
            ("≝", r"\(\eqqcolon\)"),
            ("≞", r"\(\leqq\)"),
            ("≟", r"\(\geqq\)"),
            ("≠", r"\(\neq\)"),
            ("≡", r"\(\equiv\)"),
            ("≤", r"\(\leq\)"),
            ("≥", r"\(\geq\)"),
            ("𝛼", r"\(\alpha\)"),
            ("𝛽", r"\(\beta\)"),
            ("𝛾", r"\(\gamma\)"),
            ("𝛿", r"\(\delta\)"),
            ("𝜀", r"\(\epsilon\)"),
            ("𝜁", r"\(\zeta\)"),
            ("𝜂", r"\(\eta\)"),
            ("𝜃", r"\(\theta\)"),
            ("𝜉", r"\(\xi\)"),
            ("𝜊", r"\(\iota\)"),
            ("𝜋", r"\(\pi\)"),
            ("𝜌", r"\(\rho\)"),
            ("𝜎", r"\(\sigma\)"),
            ("𝜏", r"\(\tau\)"),
            ("𝜐", r"\(\upsilon\)"),
            ("𝜑", r"\(\phi\)"),
            ("𝜒", r"\(\chi\)"),
            ("𝜓", r"\(\psi\)"),
            ("𝜔", r"\(\omega\)"),
            ("𝐸", r"\(E\)"),
            ("×", r"\(\times\)"),
            ("’", r"'"),
            ("ℎ", r"\(h\)"),
            ("𝑇", r"\(T\)"),
            ("𝐼", r"\(I\)"),
            ("Γ", r"\(\Gamma\)"),
            ("⟦", r"\( [\![ \)"),
            ("⟧", r"\( ]\!] \)"),
            ("⚠️", "Attention"),
            ("≼", r"\(\preceq\)"),
            ("⊕", r"\(\oplus\)"),
            ("∗", r"*"),
            ("★", r"*"),
            ("🖋️", "démo"),
            ("𝐹", r"\(F\)"),
            ("𝐻", r"\(H\)"),
            ("⏺️", ""),
            ("ℓ", r"\(\ell\)"),
            ("𝑃", r"\(P\)"),
            ("𝐴", r"\(A\)"),
            ("⊔", r"\(\sqcup\)"),
            ("🌈", "arc-en-ciel"),
            ("⌊", r"\(\lfloor\)"),
            ("⌋", r"\(\rfloor\)"),
            ("𝐵", r"\(B\)"),
            ("𝐺", r"\(G\)"),
            ("⩾", r"\(\geqslant\)"),
            ("🪜", "échelle"),
            ("🪢", "nœud"),
            ("🔗", "lien"),
            ("🍕", "pizza"),
            ("🗯️", "bulle de dialogue"),
            ("🧱", "brique"),
            ("📽️", "projecteur"),
            ("⭕", "cercle rouge"),
            ("✅", "coche verte"),
            ("🟰", "s"),
            ("⏹️", "stop"),
            ("〰️", "zigzag"),
            ("·", r"."),

        ]

        for old, new in list_of_subs:
            text = text.replace(old, new)

        
        # Étape 1.5: Retirer les délimiteurs \[...\] ou \(...\) autour des environnements mathématiques
        # Ces environnements créent déjà leur propre contexte mathématique et ne doivent PAS être
        # encapsulés dans des délimiteurs supplémentaires
        # Pattern pour capturer les environnements mathématiques complets
        env_names = r'align\*?|equation\*?|gather\*?|multline\*?|split|eqnarray\*?'
        
        # Retirer \[...\] autour des environnements
        text = re.sub(
            r'\\\[\s*\\begin\{(' + env_names + r')\}(.*?)\\end\{\1\}\s*\\\]',
            r'\\begin{\1}\2\\end{\1}',
            text,
            flags=re.DOTALL
        )
        
        # Retirer \(...\) autour des environnements
        text = re.sub(
            r'\\\(\s*\\begin\{(' + env_names + r')\}(.*?)\\end\{\1\}\s*\\\)',
            r'\\begin{\1}\2\\end{\1}',
            text,
            flags=re.DOTALL
        )
        
        # Étape 2: Sauvegarder les environnements mathématiques LaTeX (align, equation, etc.)
        # Ces environnements ne doivent PAS être dans des délimiteurs \[...\] ou $...$
        math_environments = []
        env_pattern = r'\\begin\{(align\*?|equation\*?|gather\*?|multline\*?|split|eqnarray\*?)\}(.*?)\\end\{\1\}'
        
        def save_math_env(match):
            math_environments.append(match.group(0))
            return f"<<<MATH_ENV_{len(math_environments)-1}>>>"
        
        text = re.sub(env_pattern, save_math_env, text, flags=re.DOTALL)
        
        # Étape 3: Retirer les délimiteurs \[...\] ou \(...\) autour des placeholders d'environnements
        # Cela gère les cas résiduels où Anki a mis des délimiteurs
        text = re.sub(r'\\\[\s*(<<<MATH_ENV_\d+>>>)\s*\\\]', r'\1', text)
        text = re.sub(r'\\\(\s*(<<<MATH_ENV_\d+>>>)\s*\\\)', r'\1', text)
        
        # Étape 4: Convertir les balises MathJax \(...\) et \[...\]
        # D'abord retirer ces balises des spans HTML
        text = re.sub(r'<span class="math-tex">\\\((.*?)\\\)</span>', r'\\\(\1\\\)', text, flags=re.DOTALL)
        text = re.sub(r'<span class="math-tex">\\\[(.*?)\\\]</span>', r'\\\[\1\\\]', text, flags=re.DOTALL)
        
        # Étape 4.5: Extraire les environnements mathématiques des délimiteurs \(...\) et \[...\]
        # IMPORTANT: Cette étape doit se faire AVANT la conversion de \(...\) en $...$
        # Gérer les cas où un environnement est dans un délimiteur avec du contenu avant/après
        # Ex: \(\tilde P : \quad \Biggl | \space <<<MATH_ENV_X>>>\) 
        #     devient \(\tilde P : \quad \Biggl | \space\) <<<MATH_ENV_X>>>
        
        def extract_env_from_inline_delimiters(match):
            """Extrait les environnements mathématiques des délimiteurs \(...\)"""
            content = match.group(1)
            
            # Chercher les placeholders d'environnements
            env_pattern = r'(.*?)(<<<MATH_ENV_\d+>>>)(.*)'
            env_match = re.search(env_pattern, content, re.DOTALL)
            
            if not env_match:
                return match.group(0)
            
            before = env_match.group(1).strip()
            env_placeholder = env_match.group(2)
            after = env_match.group(3).strip()
            
            # Reconstruire
            parts = []
            if before:
                parts.append(f'\\({before}\\)')
            parts.append(env_placeholder)
            if after:
                parts.append(f'\\({after}\\)')
            
            return ' '.join(parts) if parts else env_placeholder
        
        def extract_env_from_display_delimiters(match):
            """Extrait les environnements mathématiques des délimiteurs \[...\]"""
            content = match.group(1)
            
            # Chercher les placeholders d'environnements
            env_pattern = r'(.*?)(<<<MATH_ENV_\d+>>>)(.*)'
            env_match = re.search(env_pattern, content, re.DOTALL)
            
            if not env_match:
                return match.group(0)
            
            before = env_match.group(1).strip()
            env_placeholder = env_match.group(2)
            after = env_match.group(3).strip()
            
            # Reconstruire
            parts = []
            if before:
                parts.append(f'\\[{before}\\]')
            parts.append(env_placeholder)
            if after:
                parts.append(f'\\[{after}\\]')
            
            return '\n'.join(parts) if parts else env_placeholder
        
        # Traiter les \(...\) contenant des environnements (AVANT conversion en $...$)
        text = re.sub(
            r'\\\(((?:(?!\\\(|\\\)).)*<<<MATH_ENV_\d+>>>(?:(?!\\\(|\\\)).)*)\\\)',
            extract_env_from_inline_delimiters,
            text,
            flags=re.DOTALL
        )
        
        # Traiter les \[...\] contenant des environnements
        text = re.sub(
            r'\\\[(.*?<<<MATH_ENV_\d+>>>.*?)\\\]',
            extract_env_from_display_delimiters,
            text,
            flags=re.DOTALL
        )
        
        # Étape 5: Maintenant convertir \(...\) en $...$ et \[...\] en \[...\]
        text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
        text = re.sub(r'\\\[(.*?)\\\]', r'\n\\[\1\\]\n', text, flags=re.DOTALL)
        
        # Étape 6: Convertir les balises HTML basiques
        text = re.sub(r'<strong>(.*?)</strong>', r'\\textbf{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<b>(.*?)</b>', r'\\textbf{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<em>(.*?)</em>', r'\\textit{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<i>(.*?)</i>', r'\\textit{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<u>(.*?)</u>', r'\\underline{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<sup>(.*?)</sup>', r'\\textsuperscript{\1}', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<sub>(.*?)</sub>', r'\\textsubscript{\1}', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Étape 7: Convertir les images
        text = self._convert_images(text)
        
        # Étape 8: Convertir les listes
        text = self._convert_lists(text)
        
        # Étape 9: Convertir les sauts de ligne
        text = re.sub(r'<br\s*/?>', r'\n\n', text)
        text = re.sub(r'<div>(.*?)</div>', r'\1\n\n', text, flags=re.DOTALL)
        
        # Étape 10: Nettoyer les autres balises HTML
        # text = re.sub(r'<[^>]+>', '', text)
        
        # Étape 11: Échapper les caractères spéciaux LaTeX (sauf dans les maths)
        text = self._escape_latex_special_chars(text)
        
        # Étape 12: Nettoyer les lignes vides dans les environnements mathématiques sauvegardés
        cleaned_math_environments = []
        for env in math_environments:
            # Supprimer les lignes vides à l'intérieur des environnements mathématiques
            cleaned_env = re.sub(r'\n\s*\n+', r'\n', env)
            cleaned_math_environments.append(cleaned_env)
        
        # Restaurer les environnements mathématiques nettoyés
        for i, env in enumerate(cleaned_math_environments):
            text = text.replace(f"<<<MATH_ENV_{i}>>>", f'\n{env}\n')
        
        # Étape 13: Nettoyer les retours à la ligne inutiles dans les commandes LaTeX
        # Supprimer les retours à la ligne avant les accolades fermantes
        text = re.sub(r'\n\s*}', r'}', text)
        # Supprimer les retours à la ligne après les accolades ouvrantes suivies d'espaces
        text = re.sub(r'{\n\s+', r'{', text)
        
        # Étape 14: Nettoyer les lignes vides dans les environnements mathématiques \[ \]
        # LaTeX n'accepte pas de lignes vides dans ces environnements
        def clean_display_math(match):
            content = match.group(1)
            # Supprimer toutes les lignes vides à l'intérieur
            cleaned = re.sub(r'\n\s*\n+', r'\n', content)
            return r'\[' + cleaned + r'\]'
        
        text = re.sub(r'\\\[(.*?)\\\]', clean_display_math, text, flags=re.DOTALL)
        
        # Nettoyer aussi les lignes vides dans les environnements inline $ $
        def clean_inline_math(match):
            content = match.group(1)
            # Supprimer toutes les lignes vides à l'intérieur
            cleaned = re.sub(r'\n\s*\n+', r' ', content)
            return r'$' + cleaned + r'$'
        
        text = re.sub(r'\$(.*?)\$', clean_inline_math, text, flags=re.DOTALL)
        
        # Étape 15: Nettoyer les espaces multiples et les lignes vides
        text = re.sub(r'\n\n\n+', r'\n\n', text)
        text = text.strip()

        return text
    
    def _convert_images(self, text):
        """Convertit les balises <img> en commandes LaTeX \ includegraphics"""
        if not self.anki_connector or not self.images_dir:
            # Si pas de support d'images, simplement retirer les balises
            return re.sub(r'<img[^>]*>', '', text, flags=re.IGNORECASE)
        
        def convert_img(match):
            # Extraire le nom du fichier depuis src="..."
            img_tag = match.group(0)
            src_match = re.search(r'src=["\']([^"\'^>]+)["\']', img_tag, re.IGNORECASE)
            
            if not src_match:
                return ''  # Pas de src trouvé, ignorer l'image
            
            filename = src_match.group(1)
            
            # Extraire les attributs optionnels (width, height)
            width_match = re.search(r'width=["\']([^"\'^>]+)["\']', img_tag, re.IGNORECASE)
            height_match = re.search(r'height=["\']([^"\'^>]+)["\']', img_tag, re.IGNORECASE)
            
            # Récupérer et sauvegarder l'image si pas déjà fait
            if filename not in self.processed_images:
                try:
                    # Récupérer le fichier depuis Anki
                    media_data = self.anki_connector.retrieve_media_file(filename)
                    
                    if media_data:
                        # Décoder base64 et sauvegarder
                        image_data = base64.b64decode(media_data)
                        
                        # Créer le dossier images s'il n'existe pas
                        self.images_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Sauvegarder l'image
                        image_path = self.images_dir / filename
                        with open(image_path, 'wb') as f:
                            f.write(image_data)
                        
                        self.processed_images.add(filename)
                except Exception as e:
                    print(f"  ⚠ Erreur lors de la récupération de l'image '{filename}': {e}")
                    return ''  # Ignorer l'image en cas d'erreur
            
            # Générer la commande LaTeX
            options = []
            if width_match:
                width = width_match.group(1)
                # Convertir les pixels en cm (approximation: 1px ≈ 0.0264583cm)
                if width.endswith('px'):
                    width_px = int(width.replace('px', ''))
                    width_cm = width_px * 0.0264583
                    options.append(f'width={width_cm:.2f}cm')
                else:
                    options.append(f'width={width}')
            
            if height_match:
                height = height_match.group(1)
                if height.endswith('px'):
                    height_px = int(height.replace('px', ''))
                    height_cm = height_px * 0.0264583
                    options.append(f'height={height_cm:.2f}cm')
                else:
                    options.append(f'height={height}')
            
            # Si pas de dimensions spécifiées, utiliser une largeur par défaut
            if not options:
                options.append('width=0.8\\textwidth')
            
            options_str = ','.join(options)
            
            # Retourner la commande LaTeX (chemin relatif vers le dossier images)
            return f'\n\n\\begin{{center}}\n\\includegraphics[{options_str}]{{images/{filename}}}\n\\end{{center}}\n\n'
        
        # Remplacer toutes les balises <img>
        text = re.sub(r'<img[^>]*>', convert_img, text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def _convert_lists(text):
        """Convertit les listes HTML en listes LaTeX"""
        # Listes non ordonnées
        def convert_ul(match):
            content = match.group(1)
            # Utiliser [^>]* pour capturer les balises <li> avec ou sans attributs
            items = re.findall(r'<li[^>]*>(.*?)</li>', content, flags=re.DOTALL | re.IGNORECASE)
            if not items:
                # Fallback: essayer sans la balise fermante (certains HTML mal formés)
                items = re.findall(r'<li[^>]*>(.*?)(?=<li|</ul>|$)', content, flags=re.DOTALL | re.IGNORECASE)
            
            latex_items = '\n'.join([f'  \\item {item.strip()}' for item in items if item.strip()])
            # Ignorer les listes vides
            if not latex_items.strip():
                return ''
            return f'\\begin{{itemize}}\n{latex_items}\n\\end{{itemize}}'
        
        text = re.sub(r'<ul[^>]*>(.*?)</ul>', convert_ul, text, flags=re.DOTALL | re.IGNORECASE)
        
        # Listes ordonnées
        def convert_ol(match):
            content = match.group(1)
            # Utiliser [^>]* pour capturer les balises <li> avec ou sans attributs
            items = re.findall(r'<li[^>]*>(.*?)</li>', content, flags=re.DOTALL | re.IGNORECASE)
            if not items:
                # Fallback: essayer sans la balise fermante
                items = re.findall(r'<li[^>]*>(.*?)(?=<li|</ol>|$)', content, flags=re.DOTALL | re.IGNORECASE)
            
            latex_items = '\n'.join([f'  \\item {item.strip()}' for item in items if item.strip()])
            # Ignorer les listes vides
            if not latex_items.strip():
                return ''
            return f'\\begin{{enumerate}}\n{latex_items}\n\\end{{enumerate}}'
        
        text = re.sub(r'<ol[^>]*>(.*?)</ol>', convert_ol, text, flags=re.DOTALL | re.IGNORECASE)
        
        return text
    
    def _escape_latex_special_chars(self, text):
        """Échappe les caractères spéciaux LaTeX en dehors des zones mathématiques"""
        # Protéger les zones mathématiques
        math_inline = []
        math_display = []
        
        def save_inline(match):
            math_inline.append(match.group(0))
            return f"<<<MATH_INLINE_{len(math_inline)-1}>>>"
        
        def save_display(match):
            math_display.append(match.group(0))
            return f"<<<MATH_DISPLAY_{len(math_display)-1}>>>"
        
        text = re.sub(r'\$.*?\$', save_inline, text, flags=re.DOTALL)
        text = re.sub(r'\\\[.*?\\\]', save_display, text, flags=re.DOTALL)
        
        """ Ne fonctionne pas si msi à cet endroit 
        # Échapper les caractères spéciaux
        chars_to_escape = ['%', '#', '_', '{', '}']
        for char in chars_to_escape:
            text = text.replace(char, '\\' + char)
        """
        
        # Restaurer les zones mathématiques
        for i, math in enumerate(math_inline):
            text = text.replace(f"<<<MATH_INLINE_{i}>>>", math)
        for i, math in enumerate(math_display):
            text = text.replace(f"<<<MATH_DISPLAY_{i}>>>", math)
        
        return text


class ChangeDetector:
    """Détecte les changements dans les cartes Anki"""
    
    def __init__(self, cache_file='anki_cache.json'):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Charge le cache des cartes"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Sauvegarde le cache des cartes"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def _get_card_hash(self, card_data):
        """Calcule le hash d'une carte"""
        content = json.dumps(card_data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def check_changes(self, deck_name, cards):
        """Vérifie si des cartes ont changé"""
        changes = {
            'new': [],
            'modified': [],
            'deleted': []
        }
        
        current_card_ids = set()
        
        for card in cards:
            card_id = str(card['cardId'])
            current_card_ids.add(card_id)
            card_hash = self._get_card_hash(card)
            
            if deck_name not in self.cache:
                self.cache[deck_name] = {}
            
            if card_id not in self.cache[deck_name]:
                changes['new'].append(card_id)
                self.cache[deck_name][card_id] = card_hash
            elif self.cache[deck_name][card_id] != card_hash:
                changes['modified'].append(card_id)
                self.cache[deck_name][card_id] = card_hash
        
        # Détecter les cartes supprimées
        if deck_name in self.cache:
            cached_ids = set(self.cache[deck_name].keys())
            deleted_ids = cached_ids - current_card_ids
            changes['deleted'] = list(deleted_ids)
            
            for deleted_id in deleted_ids:
                del self.cache[deck_name][deleted_id]
        
        self._save_cache()
        return changes
    
    def has_changes(self, changes):
        """Vérifie s'il y a des changements"""
        return bool(changes['new'] or changes['modified'] or changes['deleted'])


class LaTeXGenerator:
    """Génère les fichiers LaTeX à partir des cartes Anki"""
    
    def __init__(self, output_dir='output', anki_connector=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.anki_connector = anki_connector
        self.images_dir = None  # Sera défini lors de la génération de chaque document
        self.converter = None  # Sera créé lors de la génération avec le bon dossier d'images
    
    def _parse_deck_hierarchy(self, deck_name, base_pattern):
        """Analyse la hiérarchie d'un paquet et retourne la profondeur et le nom nettoyé"""
        # Retirer le préfixe de base (base_pattern est une regex comme '^prépa::MPI::maths::cours::')
        relative_path = re.sub(base_pattern, '', deck_name)
        
        # Vérifier si c'est le paquet racine (pas de changement après le re.sub)
        if relative_path == deck_name:
            # C'est le paquet racine lui-même, pas de hiérarchie à créer
            return 0, []
        
        # Si le relative_path est vide, c'est aussi le paquet racine
        if not relative_path:
            return 0, []
        
        # C'est un sous-paquet, compter le nombre de parties séparées par '::'
        parts = relative_path.split('::')
        depth = len(parts)
        return depth, parts
    
    def generate_latex_class(self):
        """Génère la classe LaTeX personnalisée"""
        class_content = r"""\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ankicards}[2026/01/14 Anki Cards Class]

% Basé sur article
\LoadClass[11pt,a4paper]{article}

% Packages requis
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[french]{babel}
\RequirePackage{amsmath}
\RequirePackage{amsfonts}
\RequirePackage{amssymb}
\RequirePackage{amsthm}
\RequirePackage[margin=2cm]{geometry}
\RequirePackage{xcolor}
\RequirePackage{tcolorbox}
\RequirePackage{enumitem}
\RequirePackage{hyperref}

\RequirePackage{mathrsfs}
\RequirePackage{fancyhdr}
\RequirePackage{titlesec}
\RequirePackage{mathpazo}
\RequirePackage{fontawesome5}
\RequirePackage{graphicx}
\RequirePackage{marginnote}
\RequirePackage{needspace}
\RequirePackage{atbegshi}
\RequirePackage[normalem]{ulem}
\RequirePackage{etoolbox}

% Configuration des boîtes pour les cartes
\tcbuselibrary{skins,breakable}

\newtcolorbox{ankicard}[1][]{
  enhanced,
  breakable,
  colback=white,
  colframe=blue!75!black,
  boxrule=1pt,
  arc=3mm,
  left=5mm,
  right=5mm,
  top=5mm,
  bottom=5mm,
  #1
}

% Commande pour une carte Anki sans titre
\newcommand{\card}[1]{%
  \begin{ankicard}
    #1
  \end{ankicard}
  \vspace{5mm}
}

% Commande pour une carte Anki avec titre
\newcommand{\cardwithtitle}[2]{%
  \begin{ankicard}
    % Titre dans un rectangle en haut
    \noindent\begin{tcolorbox}[
      enhanced,
      colback=blue!10,
      colframe=blue!75!black,
      boxrule=0.5pt,
      arc=2mm,
      top=2mm,
      bottom=2mm,
      left=3mm,
      right=3mm,
      width=\linewidth,
      nobeforeafter
    ]
      { #1}
    \end{tcolorbox}
    \vspace{3mm}
    % Contenu de la carte
    #2
  \end{ankicard}
  \vspace{5mm}
}

% Commande pour une carte avec titre et champs additionnels
\newcommand{\cardwithextra}[3]{%
  \begin{ankicard}
    % Titre dans un rectangle en haut
    \noindent\begin{tcolorbox}[
      enhanced,
      colback=blue!10,
      colframe=blue!75!black,
      boxrule=0.5pt,
      arc=2mm,
      top=2mm,
      bottom=2mm,
      left=3mm,
      right=3mm,
      width=\linewidth,
      nobeforeafter
    ]
      { #1}
    \end{tcolorbox}
    \vspace{3mm}
    % Contenu de la carte
    #2
  \end{ankicard}
  % Champs additionnels en dessous du cadre
  \vspace{2mm}
  \noindent #3
  \vspace{5mm}
}

% Configuration des sections
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{3}
"""
        return class_content
        class_file = self.output_dir / 'ankicards.cls'
        with open(class_file, 'w', encoding='utf-8') as f:
            f.write(class_content)
    
    def generate_latex_document(self, deck_structure, base_pattern, output_subdir):
        """Génère le document LaTeX principal avec hiérarchie"""
        # Créer le dossier images pour ce document
        self.images_dir = output_subdir / 'images'
        
        # Créer le convertisseur avec le support des images
        self.converter = HTMLToLatexConverter(
            anki_connector=self.anki_connector,
            images_dir=self.images_dir
        )
        
        doc_content = r"""\documentclass{../ankicards}

\title{Fiches de Cours Anki}
\author{Cartes Anki}
\date{\today}

\begin{document}

\maketitle
\tableofcontents
\newpage

"""
        
        # Trier les paquets par nom pour maintenir l'ordre hiérarchique
        sorted_decks = sorted(deck_structure.items())
        
        # Garder une trace des sections déjà écrites pour éviter les doublons
        written_sections = set()
        
        for deck_name, cards in sorted_decks:
            # Analyser la hiérarchie
            depth, parts = self._parse_deck_hierarchy(deck_name, base_pattern)
            
            # Générer tous les titres de la hiérarchie qui n'ont pas encore été écrits
            for i in range(1, depth + 1):
                # Construire le chemin partiel
                partial_path = '::'.join(parts[:i])
                
                if partial_path not in written_sections:
                    written_sections.add(partial_path)
                    
                    # Déterminer le type de section selon la profondeur
                    if i == 1:
                        section_cmd = "section"
                    elif i == 2:
                        section_cmd = "subsection"
                    else:  # i >= 3
                        section_cmd = "subsubsection"
                    
                    # Nettoyer le nom (utiliser seulement la dernière partie du chemin partiel)
                    clean_name = self._clean_chapter_name(parts[i-1])
                    doc_content += f"\n\\{section_cmd}{{{clean_name}}}\n\n"
            
            # Ajouter les cartes (seulement si le paquet en a)
            if cards:
                for card in cards:
                    # Convertir le contenu
                    latex_content = self.converter.convert(card['content'])
                    
                    # Choisir la commande selon qu'il y a un titre et/ou des champs extra
                    if card.get('title') and card.get('extra_fields'):
                        # Carte avec titre et champs additionnels
                        latex_title = self.converter.convert(card['title'])
                        latex_extra = self.converter.convert(card['extra_fields'])
                        doc_content += f"\\cardwithextra{{\n{latex_title}\n}}{{\n{latex_content}\n}}{{\n{latex_extra}\n}}\n\n"
                    elif card.get('title'):
                        # Carte avec titre seulement
                        latex_title = self.converter.convert(card['title'])
                        doc_content += f"\\cardwithtitle{{\n{latex_title}\n}}{{\n{latex_content}\n}}\n\n"
                    else:
                        # Carte sans titre
                        doc_content += f"\\card{{\n{latex_content}\n}}\n\n"
        
        doc_content += r"\end{document}"
        
        return doc_content
    
    def _clean_chapter_name(self, chapter_name):
        """Nettoie le nom du chapitre pour LaTeX"""
        # Retirer le préfixe [x] - 
        name = re.sub(r'^\[\d+\]\s*-\s*', '', chapter_name)
        # Retirer les numéros du type "11.1.1 " ou "11.1 " au début
        name = re.sub(r'^\d+(\.\d+)*\s+', '', name)
        # Échapper les caractères spéciaux
        name = name.replace('_', '\\_')
        name = name.replace('%', '\\%')
        name = name.replace('#', '\\#')
        return name

def roman_to_int(s):
    """Convertit un nombre romain en entier"""
    # l'ordre est censé permettre de faire fonctionner les chiffres comme IV, IX, etc.
    roman_numerals = [
        ('M', 1000),
        ('CM', 900),
        ('D', 500),
        ('CD', 400),
        ('C', 100),
        ('XC', 90),
        ('L', 50),
        ('XL', 40),
        ('X', 10),
        ('IX', 9),
        ('V', 5),
        ('IV', 4),
        ('I', 1)
    ]

    i = 0
    num = 0 

    while i < len(s):
        for roman, value in roman_numerals:
            if s.startswith(roman, i):
                num += value
                i += len(roman)
                break
        else:
            # Aucun chiffre romain valide trouvé, ignorer le caractère
            i += 1

    # print(f"Conversion du nombre romain '{s}' en entier: {num}")
    return num

def sort_function(card, criteria=None):
    """Fonction de tri personnalisée pour les cartes"""

    if criteria.get(card["modelName"]) and 'sort_field' in criteria.get(card["modelName"]):
        criterion = criteria[card["modelName"]]['sort_field']
        field = card["fields"].get(criterion)
        if field is None:
            return 0
        else :
            try :
                # on regarde s'il s'agit d'un chiffre 
                return int(field.get('value', 0))
            except ValueError:
                # on essaye de trouver des nombres dans le champ avec une regex 
                numbers = re.findall(r'\d+', field.get('value', ''))
                if numbers:
                    nb = ""
                    for n in numbers:
                        nb += n
                    return int(nb)

                # si on arrive ici, aucun chiffre trouvé, on cherche en romains si activé                
                if criteria[card["modelName"]].get("check_roman_numbering", False):
                    return roman_to_int(re.sub(r'[^IVXLCDM]', '', field.get('value', '')))

    return 0 


def main(main_deck="prépa::MPI::maths::cours", card_types_config=None, folder_output="", compilation_pdf=False, check_doube_note=True):
    """Fonction principale
    check_double_note : si True, évite les doublons quand plusieurs cartes partagent une même note (par exemple cartes recto-verso)
    """
    print("=== Extraction des cartes Anki vers LaTeX ===\n")
    
    # Configuration par défaut si non fournie
    if card_types_config is None:
        card_types_config = {
            "maths": {
                "title_field": "Front",
                "content_field": "Back",
                "extra_fields": ["démo"]
            },
            "Simple [Bôtiful]": {
                "title_field": None,
                "content_field": "Verso",
                "extra_fields": []
            },
            "Basique": {
                "title_field": None,
                "content_field": "Verso",
                "extra_fields": []
            }
        }
    
    # Initialisation
    anki = AnkiConnector()
    detector = ChangeDetector()
    latex_gen = LaTeXGenerator(anki_connector=anki)
    
    try:
        # Récupérer tous les paquets
        print("Récupération des paquets Anki...")
        all_decks = anki.get_deck_names()
        
        # Filtrer les paquets qui correspondent au pattern main_deck::*
        # Échapper les caractères spéciaux pour la regex et ajouter le pattern de fin
        target_pattern = r'^' + re.escape(main_deck) + r'::'
        print(f"Pattern de recherche: {target_pattern}")

        target_decks = [deck for deck in all_decks if re.match(target_pattern, deck)]
        
        # Ajouter le paquet racine lui-même s'il existe (pour les cartes directement dans le paquet principal)
        if main_deck in all_decks:
            target_decks.insert(0, main_deck)  # Insérer au début pour garder l'ordre hiérarchique
        
        if not target_decks:
            print("Aucun paquet trouvé correspondant au pattern 'prépa::MPI::maths::cours::*'")
            print(f"Paquets disponibles: {all_decks}")
            return
        
        print(f"Paquets trouvés: {len(target_decks)}")
        # for deck in target_decks:
        #     print(f"  - {deck}")
            
        
        # Extraire les cartes par chapitre en évitant les doublons
        deck_structure = {}  # Structure: {deck_name: [cards]}
        all_changes = {}
        unsupported_types = {}  # Pour tracker les types de notes non pris en charge
        processed_card_ids = set()  # Pour éviter les doublons
        processed_note_ids = set() # Pour éviter les doublons quand plusieurs cartes partagent une même note
        # (par exemple cartes recto-verso)

        # extraie toutes les cartes en une seule requête (trop long de faire paqiet par paquet )
        all_cards = anki.get_cards_by_subdeck(main_deck)
        
        print("\nExtraction des cartes...")
        for deck_name in target_decks:
            print(f"\nTraitement du paquet: {deck_name}")
            
            if not (deck_name in all_cards):
                print(f"  0 carte(s) trouvée(s)")
                deck_structure[deck_name] = []
                continue
            
            cards = all_cards[deck_name]
            print(f"  {len(cards)} carte(s) trouvée(s) (brut)")
            
            # Vérifier les changements
            changes = detector.check_changes(deck_name, cards)
            if detector.has_changes(changes):
                all_changes[deck_name] = changes
                print(f"  ⚠ Modifications détectées:")
                if changes['new']:
                    print(f"    - Nouvelles: {len(changes['new'])}")
                if changes['modified']:
                    print(f"    - Modifiées: {len(changes['modified'])}")
                if changes['deleted']:
                    print(f"    - Supprimées: {len(changes['deleted'])}")
            
            # Extraire le champ Back de chaque carte (en évitant les doublons)
            deck_cards = []

            cards.sort(key=(lambda card: sort_function(card, criteria=card_types_config)))

            for card in cards:
                # print(card)
                # for k, v in card.items():
                #    print(f"   {k}: {v}")

                # raise ValueError("Debug stop")
                card_id = card['cardId']
                note_id = card['note']
                
                # Vérifier que la carte appartient exactement à ce paquet (pas à un sous-paquet)
                # En vérifiant le deckName de la carte
                if card.get('deckName') != deck_name:
                    continue
                
                # Vérifier si déjà traitée
                if card_id in processed_card_ids or (check_doube_note and note_id in processed_note_ids):
                    continue
                
                processed_card_ids.add(card_id)
                processed_note_ids.add(note_id)
                
                # Récupérer la configuration pour ce type de carte
                model_name = card['modelName']
                if model_name not in card_types_config:
                    # Tracker les types non pris en charge
                    if model_name not in unsupported_types:
                        unsupported_types[model_name] = 0
                    unsupported_types[model_name] += 1
                    continue
                
                config = card_types_config[model_name]
                
                # Extraire le contenu principal
                content_field = config['content_field']
                if content_field not in card['fields']:
                    print(f"  ⚠ Champ '{content_field}' introuvable dans la carte, carte ignorée")
                    continue
                content = card['fields'][content_field]['value']
                
                # Extraire le titre si configuré
                title = None
                if config.get('title_field'):
                    title_field = config['title_field']
                    if title_field in card['fields']:
                        title = card['fields'][title_field]['value']
                
                # Extraire les champs additionnels si configurés
                extra_content = []
                for extra_field in config.get('extra_fields', []):
                    if extra_field in card['fields']:
                        if card['fields'][extra_field]['value'] != "":
                            field_value = extra_field + " " + card['fields'][extra_field]['value']
                        else :
                            field_value = card['fields'][extra_field]['value']
                        if field_value and field_value.strip():  # Ignorer les champs vides
                            extra_content.append(field_value)
                
                # Combiner les champs additionnels
                extra_fields_text = '\n\n'.join(extra_content) if extra_content else None
                
                deck_cards.append({
                    'id': card_id,
                    'content': content,
                    'title': title,
                    'extra_fields': extra_fields_text
                })
            
            print(f"  {len(deck_cards)} carte(s) unique(s) pour ce paquet")
            deck_structure[deck_name] = deck_cards
        
        # Afficher le résumé global des changements
        if all_changes:
            # Calculer les totaux globaux
            total_new = sum(len(changes['new']) for changes in all_changes.values())
            total_modified = sum(len(changes['modified']) for changes in all_changes.values())
            total_deleted = sum(len(changes['deleted']) for changes in all_changes.values())
            
            print("\n" + "="*60)
            print("⚠ RÉSUMÉ GLOBAL DES MODIFICATIONS DÉTECTÉES ⚠")
            print("="*60)
            if total_new:
                print(f"  ✓ {total_new} nouvelle(s) carte(s)")
            if total_modified:
                print(f"  ✓ {total_modified} carte(s) modifiée(s)")
            if total_deleted:
                print(f"  ✓ {total_deleted} carte(s) supprimée(s)")
            print("="*60 + "\n")
        else:
            print("\n✓ Aucune modification détectée depuis la dernière exécution\n")
        
        # Afficher les types de notes non pris en charge
        if unsupported_types:
            print("\n" + "="*60)
            print("⚠⚠⚠ TYPES DE NOTES NON PRIS EN CHARGE ⚠⚠⚠")
            print("="*60)
            total_unsupported = sum(unsupported_types.values())
            print(f"\n{total_unsupported} carte(s) ignorée(s) au total\n")
            for model_name, count in sorted(unsupported_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  • '{model_name}': {count} carte(s)")
            print("\n" + "="*60 + "\n")
        
        # dossier de sortie
        output_folder = latex_gen.output_dir / folder_output
        output_folder.mkdir(parents=True, exist_ok=True)

        # Générer la classe LaTeX
        print("Génération de la classe LaTeX...")
        classe = latex_gen.generate_latex_class()

        with open(output_folder / 'ankicards.cls', 'w', encoding='utf-8') as f:
            f.write(classe)
        
        # Générer le document LaTeX
        print("Génération du document LaTeX...")
        
        format_deck_name = main_deck.replace("::", "_")
        output_subdir = latex_gen.output_dir / format_deck_name
        output_subdir.mkdir(parents=True, exist_ok=True)
        
        latex_content = latex_gen.generate_latex_document(deck_structure, target_pattern, output_subdir)
        
        output_file = output_subdir / f'{format_deck_name}.tex'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"✓ Document LaTeX généré: {output_file}")
        
        if not compilation_pdf:
            print("\n✓ Processus terminé avec succès!")
            return
        
        # Compiler le document LaTeX
        print("\nCompilation du document LaTeX...")
        compile_latex(output_file)
        
        print("\n✓ Processus terminé avec succès!")
        
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def compile_latex(tex_file):
    """Compile le fichier LaTeX en PDF"""
    tex_path = Path(tex_file).resolve()
    
    if not tex_path.exists():
        print(f"  ✗ Le fichier {tex_path} n'existe pas")
        return
    
    try:
        # Compiler avec pdflatex (2 passages pour la table des matières)
        for i in range(2):
            print(f"  Compilation {i+1}/2...")
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', str(tex_path.name)],
                capture_output=True,
                text=True,
                cwd=str(tex_path.parent)
            )
            
            if result.returncode != 0:
                print(f"  ⚠ Avertissement lors de la compilation (code {result.returncode})")
                # Afficher les erreurs importantes
                if "!" in result.stdout:
                    errors = [line for line in result.stdout.split('\n') if line.startswith('!')]
                    for error in errors[:10]:  # Afficher jusqu'à 10 erreurs
                        print(f"    {error}")
                    
                    # Afficher aussi le contexte si possible
                    if errors:
                        print(f"\n  Pour plus de détails, consultez: {tex_path.with_suffix('.log')}")
        
        pdf_file = tex_path.with_suffix('.pdf')
        if pdf_file.exists():
            print(f"  ✓ PDF généré: {pdf_file}")
        else:
            print(f"  ⚠ Le PDF n'a pas été créé. Vérifiez les logs.")
            log_file = tex_path.with_suffix('.log')
            if log_file.exists():
                print(f"  Fichier log: {log_file}")
            
    except FileNotFoundError:
        print("  ✗ pdflatex n'est pas installé ou n'est pas dans le PATH")
        print("  → Installez une distribution LaTeX (TeX Live, MiKTeX, etc.)")
    except Exception as e:
        print(f"  ✗ Erreur lors de la compilation: {e}")


if __name__ == '__main__':
    # ========== CONFIGURATION ==========
    
    # Paquet dont on veut extraire toutes les cartes et sous-paquets
    # main_deck = "prépa::MPI::maths::cours"
    main_deck = "prépa::MPI::Francais::Citations"

    output_folder = ""

    # Si True, fait tourner le script pour chacun des sous paquets directs de main_deck
    apply_to_all_subdecks = False
    compilation_auto = True

    if apply_to_all_subdecks:
        format_deck_name = main_deck.replace("::", "_")
        output_folder = format_deck_name + "_all_subdecks"
    
    # Configuration des types de cartes Anki
    # Pour chaque type de carte (modelName), définir :
    # - title_field : le nom du champ à utiliser comme titre (ou None)
    # - content_field : le nom du champ à utiliser comme contenu principal
    # - extra_fields : liste des champs additionnels à afficher sous le cadre
    card_types_config = {
        "maths": {
            "title_field": "Front",
            "content_field": "Back",
            "extra_fields": ["type", "démo"],
            "sort_field": "type"
        },
        "Simple [Bôtiful]": {
            "title_field": "Recto",
            "content_field": "Verso",
            "extra_fields": []
        },
        "Basique": {
            "title_field": "Recto",
            "content_field": "Verso",
            "extra_fields": []
        },
        "citations" :{
            "title_field": "Recto",
            "content_field": "Verso",
            "extra_fields": ["chapitre", "page"],
            "sort_field": "page",
            "check_roman_numbering": True # prend toutes les lettres majuscules du champ et tente de faire un chiffre avec
        },
        "Généralités (deux sens)+" :{
            "title_field": "Recto",
            "content_field": "Verso",
            "extra_fields": [],
            "sort_field": "Recto",
            "check_roman_numbering": True
        },
        "Basique-2cc6f" :{
            "title_field": "Recto",
            "content_field": "Verso",
            "extra_fields": []
        },
        "Texte à trous++" :{
            "title_field": None,
            "content_field": "Texte",
            "extra_fields": []
        }, 
        "Texte à trous" :{
            "title_field": None,
            "content_field": "Texte",
            "extra_fields": ["Double verso"]
        }, 
        "Basic" :{
            "title_field": "Front",
            "content_field": "Back"
        }, 
        "Basic+++++" :{
            "title_field": "Front",
            "content_field": "Back"
        },
        "Basic++++++" :{
            "title_field": "Front",
            "content_field": "Back"
        },
        "Généralités (deux sens)++" :{
            "title_field": "Recto",
            "content_field": "Verso",
            "extra_fields": ["Contexte", "Démo"],
        },
        "Basic++++" :{
            "title_field": "Front",
            "content_field": "Back"
        },
        "Basique++++" :{
            "title_field": "Recto",
            "content_field": "Verso"
        },
        "Basique+++++" :{
            "title_field": "Recto",
            "content_field": "Verso"
        },
        "🃏++" :{
            "title_field": "Front",
            "content_field": "Back",
            "extra_fields": ["demo", "Contexte"]
        }
    }
    
    # ========== EXÉCUTION ==========


    # tests 
    if False :
        convertor = HTMLToLatexConverter()
        test_html = r"""<b>Classe C<sup>k</sup>&nbsp;de la fonction Gamma d'Euler.</b><br>\[\Gamma : x \mapsto \int_0^{+\infty} t^{x-1} e^{-t}\mathrm{d}t.\]Comment vérifier&nbsp;<b>l'hypothèse de domination</b>&nbsp;:<ol><li>La dérivée \(k\)<sup>e</sup>&nbsp;de \(x \mapsto f(x,t) = t^{x-1} e^{-t}\) est \(x \mapsto {{c1::(\ln(t))^k t^{x-1} e^{-t} }}\).&nbsp;</li><li>{{c2::On introduit un segment \([a,b] \subseteq ]0,+\infty[\), et}} pour tout \((x,t) \in {{c2::[a,b]\times ]0,+\infty[}}\) on a :\[\left|\frac{\partial^k f}{\partial x^k}(x,t)\right| = {{c1::t^{x-1}\cdot \underbrace{|\ln(t)|^k e^{-t} }_{\textrm{ne dépend pas de \(x\]} } \leqslant \left\{\begin{array}{l l}t^{a-1}|\ln(t)|^k e^{-t} &amp; \textrm{ si } t\leqslant 1,\\ t^{b-1}|\ln(t)|^k e^{-t} &amp;\textrm{ si } t\geqslant 1.\end{array}\right. }}\)</li><li>Intégrabilité au voisinage de \(0\) : {{c3::\(t^{a-1}|\ln(t)|^k e^{-t} \sim t^{a-1}|\ln(t)|^k = o\left(\frac{1}{t^{1-\frac{a}{2} } }\right)\) (croissances comparées) : intégrable car \(1-\frac{a}{2} &lt; 1\).}}</li><li>Intégrabilité au voisinage de \(+\infty\) : {{c3::\(t^{a-1}|\ln(t)|^k e^{-t} = o\left(\frac{1}{t^{2} }\right)\) (croissances comparées) : intégrable car \(2&gt;1\).}}</li></ol>"""
        #print("HTML de test:\n", test_html)
        latex = convertor.convert(test_html)
        print("\nLaTeX converti:\n", latex)
        raise ValueError("Debug stop")
    


    # extraction par sous paquets 
    if apply_to_all_subdecks:
        anki = AnkiConnector()
        subdecks = anki.get_child_decks(main_deck)
        print(f"Traitement de tous les sous-paquets de '{main_deck}': {subdecks}\n")
        
        for subdeck in subdecks:
            print(f"\n=== Traitement du paquet: {subdeck} ===\n")
            main(
                main_deck=subdeck, 
                card_types_config=card_types_config, 
                folder_output=output_folder,
                compilation_pdf=compilation_auto,
                check_doube_note=True)
    else:
        main(
            main_deck=main_deck, 
            card_types_config=card_types_config, 
            folder_output=output_folder,
            compilation_pdf=compilation_auto,
            check_doube_note=True
        )
