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

        # Étape 1: Décoder les entités HTML
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        text = text.replace('&#x27;', "'")
        text = text.replace('#', "nb")
        
        # Étape 2: Sauvegarder les environnements mathématiques LaTeX (align, equation, etc.)
        # Ces environnements ne doivent PAS être dans des délimiteurs \[...\] ou $...$
        math_environments = []
        env_pattern = r'\\begin\{(align\*?|equation\*?|gather\*?|multline\*?|split|eqnarray\*?)\}(.*?)\\end\{\1\}'
        
        def save_math_env(match):
            math_environments.append(match.group(0))
            return f"<<<MATH_ENV_{len(math_environments)-1}>>>"
        
        text = re.sub(env_pattern, save_math_env, text, flags=re.DOTALL)
        
        # Étape 3: Retirer les délimiteurs \[...\] ou \(...\) autour des placeholders d'environnements
        # Cela gère les cas où Anki a mis \[\begin{align}...\end{align}\]
        text = re.sub(r'\\\[\s*(<<<MATH_ENV_\d+>>>)\s*\\\]', r'\1', text)
        text = re.sub(r'\\\(\s*(<<<MATH_ENV_\d+>>>)\s*\\\)', r'\1', text)
        
        # Étape 4: Convertir les balises MathJax \(...\) et \[...\]
        # D'abord retirer ces balises des spans HTML
        text = re.sub(r'<span class="math-tex">\\\((.*?)\\\)</span>', r'\\\(\1\\\)', text, flags=re.DOTALL)
        text = re.sub(r'<span class="math-tex">\\\[(.*?)\\\]</span>', r'\\\[\1\\\]', text, flags=re.DOTALL)
        
        # Maintenant convertir \(...\) en $...$ et \[...\] en \[...\]
        text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
        text = re.sub(r'\\\[(.*?)\\\]', r'\n\\[\1\\]\n', text, flags=re.DOTALL)
        
        # Étape 5: Convertir les balises HTML basiques
        text = re.sub(r'<strong>(.*?)</strong>', r'\\textbf{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<b>(.*?)</b>', r'\\textbf{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<em>(.*?)</em>', r'\\textit{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<i>(.*?)</i>', r'\\textit{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<u>(.*?)</u>', r'\\underline{\1}', text, flags=re.DOTALL)
        
        # Étape 5: Convertir les images
        text = self._convert_images(text)
        
        # Étape 6: Convertir les listes
        text = self._convert_lists(text)
        
        # Étape 7: Convertir les sauts de ligne
        text = re.sub(r'<br\s*/?>', r'\n\n', text)
        text = re.sub(r'<div>(.*?)</div>', r'\1\n\n', text, flags=re.DOTALL)
        
        # Étape 8: Nettoyer les autres balises HTML
        # text = re.sub(r'<[^>]+>', '', text)
        
        # Étape 10: Échapper les caractères spéciaux LaTeX (sauf dans les maths)
        text = self._escape_latex_special_chars(text)
        
        # Étape 11: Restaurer les environnements mathématiques (align, equation, etc.)
        for i, env in enumerate(math_environments):
            text = text.replace(f"<<<MATH_ENV_{i}>>>", f'\n{env}\n')
        
        # Étape 12: Nettoyer les espaces multiples et les lignes vides
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
        
        # Vérifier si on a bien retiré quelque chose
        if not relative_path or relative_path == deck_name:
            # Le paquet ne correspond pas au pattern, le retourner tel quel
            parts = deck_name.split('::')
        else:
            # Compter le nombre de parties séparées par '::'
            parts = relative_path.split('::')
        
        depth = len(parts)
        return depth, parts
    
    def generate_latex_class(self):
        """Génère la classe LaTeX personnalisée"""
        class_content = r"""\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{../ankicards}[2026/01/14 Anki Cards Class]

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
      {\bfseries #1}
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
      {\bfseries #1}
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

\title{Fiches de Cours - Mathématiques MPI}
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
                    print(f"  ⚠ Type de carte '{model_name}' non configuré, carte ignorée")
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
        
        # Afficher le résumé des changements
        if all_changes:
            print("\n" + "="*60)
            print("⚠ RÉSUMÉ DES MODIFICATIONS DÉTECTÉES ⚠")
            print("="*60)
            for deck, changes in all_changes.items():
                print(f"\n{deck}:")
                if changes['new']:
                    print(f"  ✓ {len(changes['new'])} nouvelle(s) carte(s)")
                if changes['modified']:
                    print(f"  ✓ {len(changes['modified'])} carte(s) modifiée(s)")
                if changes['deleted']:
                    print(f"  ✓ {len(changes['deleted'])} carte(s) supprimée(s)")
            print("="*60 + "\n")
        else:
            print("\n✓ Aucune modification détectée depuis la dernière exécution\n")
        
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
    main_deck = "prépa::MPI::maths::cours::[13] - Probabilités"

    output_folder = ""

    # Si True, fait tourner le script pour chacun des sous paquets directs de main_deck
    apply_to_all_subdecks = False

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
            "extra_fields": ["démo"]
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
            "extra_fields": ["chapitre", "page"]
        },
        "Généralités (deux sens)+" :{
            "title_field": "Recto",
            "content_field": "Verso",
            "extra_fields": []
        }
    }
    
    # ========== EXÉCUTION ==========

    if apply_to_all_subdecks:
        anki = AnkiConnector()
        subdecks = anki.get_child_decks(main_deck)
        print(f"Traitement de tous les sous-paquets de '{main_deck}': {subdecks}\n")
        
        for subdeck in subdecks:
            print(f"\n=== Traitement du paquet: {subdeck} ===\n")
            main(subdeck, card_types_config, folder_output=output_folder)
    else:
        main(
            main_deck=main_deck, 
            card_types_config=card_types_config, 
            folder_output=output_folder,
            compilation_pdf=True,
            check_doube_note=True
        )
