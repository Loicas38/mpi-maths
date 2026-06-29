#!/usr/bin/env python3
"""
Script complet pour remplacer les raccourcis LaTeX par leurs définitions complètes.
Version avancée qui gère les commandes avec et sans arguments.
"""



import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def parse_newcommand(line: str) -> Tuple[str, str, int]:
    """Parse une ligne contenant \newcommand."""
    # Pattern pour \newcommand{\nom}[nb_args]{définition}
    pattern_with_args = r'\\newcommand\{\\([^}]+)\}\[(\d+)\]\{(.*)\}'
    # Pattern pour \newcommand{\nom}{définition}
    pattern_no_args = r'\\newcommand\{\\([^}]+)\}\{(.*)\}'
    
    match_args = re.search(pattern_with_args, line)
    if match_args:
        name = match_args.group(1)
        nb_args = int(match_args.group(2))
        definition = match_args.group(3)
        return name, definition, nb_args
    
    match_no_args = re.search(pattern_no_args, line)
    if match_no_args:
        name = match_no_args.group(1)
        definition = match_no_args.group(2)
        return name, definition, 0
    
    return None, None, 0


def parse_sty_file(sty_path: str) -> Dict[str, Tuple[str, int]]:
    """Parse un fichier .sty pour extraire tous les raccourcis."""
    shortcuts = {}
    
    try:
        with open(sty_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Traiter les commandes multi-lignes
        lines = content.split('\n')
        processed_lines = []
        current_line = ""
        brace_count = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('%'):
                continue
                
            current_line += " " + line if current_line else line
            brace_count += line.count('{') - line.count('}')
            
            if brace_count == 0 and current_line:
                processed_lines.append(current_line)
                current_line = ""
        
        # Parser chaque ligne
        for line in processed_lines:
            name, definition, nb_args = parse_newcommand(line)
            if name:
                shortcuts[name] = (definition, nb_args)
                print(f"Raccourci trouvé: \\{name} -> {definition} (args: {nb_args})")
                
    except FileNotFoundError:
        print(f"Erreur: Le fichier {sty_path} n'existe pas.")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier .sty: {e}")
        sys.exit(1)
        
    return shortcuts


def find_balanced_braces(text: str, start_pos: int) -> Tuple[Optional[str], int]:
    """
    Trouve le contenu entre accolades équilibrées à partir de start_pos.
    
    Args:
        text: Le texte à analyser
        start_pos: Position de départ (doit pointer sur '{')
        
    Returns:
        (contenu_entre_accolades, position_après_accolade_fermante)
        Retourne (None, start_pos) si pas d'accolade trouvée
    """
    if start_pos >= len(text) or text[start_pos] != '{':
        return None, start_pos
    
    brace_count = 0
    i = start_pos
    
    while i < len(text):
        if text[i] == '\\' and i + 1 < len(text):
            # Ignorer le caractère échappé
            i += 2
            continue
        elif text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                return text[start_pos + 1:i], i + 1
        i += 1
    
    # Accolades non équilibrées
    return None, start_pos


def extract_command_arguments(text: str, start_pos: int, nb_args: int) -> Tuple[List[str], int]:
    """
    Extrait les arguments d'une commande LaTeX.
    
    Args:
        text: Le texte complet
        start_pos: Position après le nom de la commande
        nb_args: Nombre d'arguments attendus
        
    Returns:
        (liste_des_arguments, position_après_dernier_argument)
    """
    args = []
    current_pos = start_pos
    
    for _ in range(nb_args):
        # Ignorer les espaces et sauts de ligne
        while current_pos < len(text) and text[current_pos].isspace():
            current_pos += 1
        
        if current_pos >= len(text):
            break
        
        # Extraire l'argument entre accolades
        arg_content, next_pos = find_balanced_braces(text, current_pos)
        if arg_content is not None:
            args.append(arg_content)
            current_pos = next_pos
        else:
            break
    
    return args, current_pos


def replace_shortcuts_advanced(text: str, shortcuts: Dict[str, Tuple[str, int]]) -> str:
    """
    Remplace tous les raccourcis dans le texte par leurs définitions.
    Version avancée qui gère les arguments.
    """
    result = text
    
    # Trier par longueur décroissante pour éviter les remplacements partiels
    sorted_shortcuts = sorted(shortcuts.items(), key=lambda x: len(x[0]), reverse=True)
    
    for name, (definition, nb_args) in sorted_shortcuts:
        command = f"\\{name}"
        
        if nb_args == 0:
            # Commandes sans arguments - méthode simple et robuste
            parts = []
            remaining = result
            
            while command in remaining:
                pos = remaining.find(command)
                if pos == -1:
                    break
                
                # Vérifier que c'est une commande complète
                end_pos = pos + len(command)
                if end_pos < len(remaining) and remaining[end_pos].isalpha():
                    # Ce n'est pas une commande complète
                    parts.append(remaining[:pos + len(command)])
                    remaining = remaining[pos + len(command):]
                    continue
                
                # Remplacer la commande
                parts.append(remaining[:pos])
                parts.append(definition)
                remaining = remaining[end_pos:]
            
            parts.append(remaining)
            result = ''.join(parts)
            
        else:
            # Commandes avec arguments - méthode plus complexe
            new_result = ""
            pos = 0
            
            while pos < len(result):
                # Chercher la prochaine occurrence de la commande
                next_pos = result.find(command, pos)
                if next_pos == -1:
                    # Plus d'occurrences, ajouter le reste
                    new_result += result[pos:]
                    break
                
                # Vérifier que c'est une commande complète
                command_end = next_pos + len(command)
                if command_end < len(result) and result[command_end].isalpha():
                    # Ce n'est pas une commande complète
                    new_result += result[pos:command_end]
                    pos = command_end
                    continue
                
                # Ajouter le texte avant la commande
                new_result += result[pos:next_pos]
                
                # Extraire les arguments
                args, args_end = extract_command_arguments(result, command_end, nb_args)
                
                if len(args) == nb_args:
                    # Remplacer les placeholders dans la définition
                    expanded = definition
                    for i, arg in enumerate(args):
                        placeholder = f"#{i + 1}"
                        expanded = expanded.replace(placeholder, arg)
                    
                    new_result += expanded
                    pos = args_end
                else:
                    # Pas assez d'arguments trouvés, garder la commande originale
                    new_result += result[next_pos:command_end]
                    pos = command_end
            
            result = new_result
    
    return result


def process_tex_file(tex_path: str, shortcuts: Dict[str, Tuple[str, int]], output_path: str = None):
    """Traite un fichier .tex en remplaçant les raccourcis."""
    try:
        with open(tex_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Remplacer les raccourcis
        expanded_content = replace_shortcuts_advanced(content, shortcuts)
        
        # Déterminer le fichier de sortie
        if output_path is None:
            tex_file = Path(tex_path)
            output_path = tex_file.parent / f"{tex_file.stem}_expanded{tex_file.suffix}"
        
        # Écrire le résultat
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(expanded_content)
            
        print(f"Fichier traité avec succès: {output_path}")
        
        # Statistiques
        original_size = len(content)
        expanded_size = len(expanded_content)
        print(f"Taille originale: {original_size} caractères")
        print(f"Taille après expansion: {expanded_size} caractères")
        print(f"Différence: {expanded_size - original_size:+d} caractères")
        
        # Compter les remplacements
        total_replacements = 0
        for name, (definition, nb_args) in shortcuts.items():
            command = f"\\{name}"
            count_before = content.count(command)
            count_after = expanded_content.count(command)
            replacements = count_before - count_after
            if replacements > 0:
                print(f"  \\{name}: {replacements} remplacements")
                total_replacements += replacements
        
        print(f"Total des remplacements: {total_replacements}")
        
    except FileNotFoundError:
        print(f"Erreur: Le fichier {tex_path} n'existe pas.")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors du traitement du fichier .tex: {e}")
        sys.exit(1)


def main(tex_file, sty_file, output_file=None):
    print("=== Expansion des raccourcis LaTeX (version complète) ===")
    print(f"Fichier raccourcis: {sty_file}")
    print(f"Fichier à traiter: {tex_file}")
    print()
    
    # Parser le fichier .sty
    print("Lecture des raccourcis...")
    shortcuts = parse_sty_file(sty_file)
    print(f"Nombre de raccourcis trouvés: {len(shortcuts)}")
    
    # Séparer par type
    no_args = sum(1 for _, (_, nb_args) in shortcuts.items() if nb_args == 0)
    with_args = len(shortcuts) - no_args
    print(f"  - Sans arguments: {no_args}")
    print(f"  - Avec arguments: {with_args}")
    print()
    
    # Traiter le fichier .tex
    print("Traitement du fichier .tex...")
    process_tex_file(tex_file, shortcuts, output_file)


if __name__ == "__main__":
    main()
