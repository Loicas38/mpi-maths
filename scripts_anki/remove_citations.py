#!/usr/bin/env python3
"""
Script pour supprimer les annotations [cite: ...] des fichiers LaTeX.
Usage: python remove_citations.py <fichier.tex>
       python remove_citations.py <fichier.tex> -o <fichier_sortie.tex>
"""

import re
import sys
import argparse
from pathlib import Path


def remove_citations(text):
    """
    Supprime toutes les annotations du type [cite: 78] ou [cite: 88, 89].
    
    Args:
        text: Le contenu du fichier LaTeX
        
    Returns:
        Le texte nettoyé sans les citations
    """
    # Pattern pour matcher [cite: liste de nombres séparés par des virgules]
    pattern = r'\[cite:\s*\d+(?:,\s*\d+)*\]'
    
    # Supprime toutes les occurrences
    cleaned_text = re.sub(pattern, '', text)
    
    # Nettoie les espaces multiples qui pourraient résulter de la suppression
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)
    
    return cleaned_text


def main():
    parser = argparse.ArgumentParser(
        description='Supprime les annotations [cite: ...] des fichiers LaTeX'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Fichier LaTeX à traiter'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Fichier de sortie (par défaut: écrase le fichier d\'entrée)'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Créer une sauvegarde du fichier original (.bak)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    
    # Vérifier que le fichier existe
    if not input_path.exists():
        print(f"Erreur: Le fichier '{args.input_file}' n'existe pas.", file=sys.stderr)
        sys.exit(1)
    
    # Lire le contenu du fichier
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Compter les occurrences avant suppression
    pattern = r'\[cite:\s*\d+(?:,\s*\d+)*\]'
    count = len(re.findall(pattern, content))
    
    # Supprimer les citations
    cleaned_content = remove_citations(content)
    
    # Déterminer le fichier de sortie
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path
        if args.backup:
            backup_path = input_path.with_suffix(input_path.suffix + '.bak')
            try:
                input_path.rename(backup_path)
                print(f"Sauvegarde créée: {backup_path}")
            except Exception as e:
                print(f"Erreur lors de la création de la sauvegarde: {e}", file=sys.stderr)
                sys.exit(1)
    
    # Écrire le résultat
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"✓ {count} citation(s) supprimée(s) de '{input_path}'")
        if args.output:
            print(f"✓ Résultat écrit dans '{output_path}'")
        else:
            print(f"✓ Fichier '{output_path}' mis à jour")
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
