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


class HTMLToLatexConverter:
    """Convertit du HTML et MathJax en LaTeX"""
    
    @staticmethod
    def convert(html_content):
        """Convertit le contenu HTML/MathJax en LaTeX"""
        if not html_content:
            return ""
        
        text = html_content
        
        # Convertir les balises MathJax
        # \(...\) pour inline math
        text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
        # \[...\] pour display math
        text = re.sub(r'\\\[(.*?)\\\]', r'\n\\[\1\\]\n', text, flags=re.DOTALL)
        
        # Convertir les balises HTML mathématiques alternatives
        text = re.sub(r'<span class="math-tex">\\\((.*?)\\\)</span>', r'$\1$', text, flags=re.DOTALL)
        text = re.sub(r'<span class="math-tex">\\\[(.*?)\\\]</span>', r'\n\\[\1\\]\n', text, flags=re.DOTALL)
        
        # Convertir les balises HTML basiques
        text = re.sub(r'<strong>(.*?)</strong>', r'\\textbf{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<b>(.*?)</b>', r'\\textbf{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<em>(.*?)</em>', r'\\textit{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<i>(.*?)</i>', r'\\textit{\1}', text, flags=re.DOTALL)
        text = re.sub(r'<u>(.*?)</u>', r'\\underline{\1}', text, flags=re.DOTALL)
        
        # Convertir les listes
        text = HTMLToLatexConverter._convert_lists(text)
        
        # Convertir les sauts de ligne
        text = re.sub(r'<br\s*/?>', r'\n\n', text)
        text = re.sub(r'<div>(.*?)</div>', r'\1\n\n', text, flags=re.DOTALL)
        
        # Nettoyer les autres balises HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Décoder les entités HTML
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        
        # Échapper les caractères spéciaux LaTeX (sauf dans les maths)
        text = HTMLToLatexConverter._escape_latex_special_chars(text)
        
        # Nettoyer les espaces multiples et les lignes vides
        text = re.sub(r'\n\n\n+', r'\n\n', text)
        text = text.strip()
        
        return text
    
    @staticmethod
    def _convert_lists(text):
        """Convertit les listes HTML en listes LaTeX"""
        # Listes non ordonnées
        def convert_ul(match):
            content = match.group(1)
            items = re.findall(r'<li>(.*?)</li>', content, flags=re.DOTALL)
            latex_items = '\n'.join([f'  \\item {item.strip()}' for item in items])
            return f'\\begin{{itemize}}\n{latex_items}\n\\end{{itemize}}'
        
        text = re.sub(r'<ul>(.*?)</ul>', convert_ul, text, flags=re.DOTALL)
        
        # Listes ordonnées
        def convert_ol(match):
            content = match.group(1)
            items = re.findall(r'<li>(.*?)</li>', content, flags=re.DOTALL)
            latex_items = '\n'.join([f'  \\item {item.strip()}' for item in items])
            return f'\\begin{{enumerate}}\n{latex_items}\n\\end{{enumerate}}'
        
        text = re.sub(r'<ol>(.*?)</ol>', convert_ol, text, flags=re.DOTALL)
        
        return text
    
    @staticmethod
    def _escape_latex_special_chars(text):
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
    
    def __init__(self, output_dir='output'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.converter = HTMLToLatexConverter()
    
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

% Commande pour une carte Anki
\newcommand{\card}[1]{%
  \begin{ankicard}
    #1
  \end{ankicard}
  \vspace{5mm}
}

% Configuration des sections
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{3}
"""
        
        class_file = self.output_dir / 'ankicards.cls'
        with open(class_file, 'w', encoding='utf-8') as f:
            f.write(class_content)
    
    def generate_latex_document(self, deck_structure, base_pattern):
        """Génère le document LaTeX principal avec hiérarchie"""
        doc_content = r"""\documentclass{ankicards}

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
                    latex_content = self.converter.convert(card['content'])
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


def main():
    """Fonction principale"""
    print("=== Extraction des cartes Anki vers LaTeX ===\n")
    
    # Initialisation
    anki = AnkiConnector()
    detector = ChangeDetector()
    latex_gen = LaTeXGenerator()
    
    try:
        # Récupérer tous les paquets
        print("Récupération des paquets Anki...")
        all_decks = anki.get_deck_names()
        
        # Filtrer les paquets qui correspondent au pattern prépa::MPI::maths::cours::*
        target_pattern = r'^prépa::MPI::maths::cours::'
        target_decks = [deck for deck in all_decks if re.match(target_pattern, deck)]
        
        if not target_decks:
            print("Aucun paquet trouvé correspondant au pattern 'prépa::MPI::maths::cours::*'")
            print(f"Paquets disponibles: {all_decks}")
            return
        
        print(f"Paquets trouvés: {len(target_decks)}")
        for deck in target_decks:
            print(f"  - {deck}")
        
        # Extraire les cartes par chapitre en évitant les doublons
        deck_structure = {}  # Structure: {deck_name: [cards]}
        all_changes = {}
        processed_card_ids = set()  # Pour éviter les doublons
        
        print("\nExtraction des cartes...")
        for deck_name in target_decks:
            print(f"\nTraitement du paquet: {deck_name}")
            
            # Récupérer les cartes avec le flag exact pour ce paquet uniquement
            # Utiliser une requête qui ne récupère que les cartes directement dans ce paquet
            query = f'"deck:{deck_name}"'
            card_ids = anki.invoke('findCards', query=query)
            
            if not card_ids:
                print(f"  0 carte(s) trouvée(s)")
                deck_structure[deck_name] = []
                continue
            
            cards = anki.invoke('cardsInfo', cards=card_ids)
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
                card_id = card['cardId']
                
                # Vérifier que la carte appartient exactement à ce paquet (pas à un sous-paquet)
                # En vérifiant le deckName de la carte
                if card.get('deckName') != deck_name:
                    continue
                
                # Vérifier si déjà traitée
                if card_id in processed_card_ids:
                    continue
                
                processed_card_ids.add(card_id)
                
                note = anki.get_note_info(card['note'])
                if note and 'Back' in note['fields']:
                    back_content = note['fields']['Back']['value']
                    deck_cards.append({
                        'id': card_id,
                        'content': back_content
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
        
        # Générer la classe LaTeX
        print("Génération de la classe LaTeX...")
        latex_gen.generate_latex_class()
        
        # Générer le document LaTeX
        print("Génération du document LaTeX...")
        latex_content = latex_gen.generate_latex_document(deck_structure, target_pattern)
        
        output_file = latex_gen.output_dir / 'fiches_cours.tex'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"✓ Document LaTeX généré: {output_file}")
        
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
    main()
