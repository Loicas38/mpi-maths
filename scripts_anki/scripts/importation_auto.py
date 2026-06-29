"""
Ce fichier crée un fichier .txt à partir d'un fichier tex pour anki. 
Il suffit d'importer le fichier générer dans anki et les paquets sont générées, les type de carte
gérés, les cartes remplies, .... 

De plus les abréviations présentes dans le fichier LaTeX sont remplacées par leur équivalent.
"""


import re
import os
import pickle
import argparse
import expand_shortcuts_complete

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name).replace(' ', '_')
    


def sanitize_title(title):
    """
    Nettoie les titres des paquets en remplaçant les caractères spéciaux
    """
    title = re.sub(r'\$([^$]+)\$', r'\1', title) # enlève les balises latex
    
    # supprime les opérateurs latex dans le cas \commande{lettre} -> lettre
    title = re.sub(r'\\[a-zA-Z]+\{([^}]+)\}', r'\1', title)
    
    # même chose dans le Cas 2: \commande lettre -> lettre (avec espace)
    title = re.sub(r'\\[a-zA-Z]+\s+([a-zA-Z])', r'\1', title)
    
    title = re.sub(r'\s+', ' ', title).strip()  # Remplace les espaces multiples par un seul espace
    return title  

def latex_to_html(latex):
    """ 
    converti les élémenbts latex tels que les listes à puce en html, 
    lu par anki
    """

    # Convertit les listes à puce
    latex = re.sub(r'\\begin\{itemize\}', '<ul>', latex)
    latex = re.sub(r'\\end\{itemize\}', '</ul>', latex)
    latex = re.sub(r'\\item\s*', '<li>', latex)
    
    # Convertit les listes numérotées
    latex = re.sub(r'\\begin\{enumerate\}', '<ol>', latex)
    latex = re.sub(r'\\end\{enumerate\}', '</ol>', latex)
    
    return latex

def sanitize_content(content):
    """
    nettoie les cartes en transformant les balises latex en balises mathjax
    """
    content = latex_to_html(content)

    content = re.sub(r'\\begin\{equation\}', r'\\[', content)
    content = re.sub(r'\\end\{equation\}', r'\\]', content)
    content = re.sub(r'\$\$(.*?)\$\$', r'\\[\1\\]', content)
    content = re.sub(r'\$([^$]+)\$', r'\\(\1\\)', content)
    content = re.sub(r'\\newline', '\n', content)

    return content

def load_tracking_data(output_dir):
    """
    Charge les données de suivi depuis le fichier tracking.pkl.
    Structure: {
        'last_card_number': int,  # Dernier numéro de carte importé
        'import_count': int,      # Nombre d'importations effectuées
        'card_versions': {        # Historique des versions de cartes
            card_number: {
                'title': str,
                'content': str
            }
        }
    }
    """
    tracking_file = os.path.join(output_dir, "tracking.pkl")
    
    if os.path.exists(tracking_file):
        with open(tracking_file, "rb") as f:
            return pickle.load(f)
    else:
        return {
            'last_card_number': 0,
            'import_count': 0,
            'card_versions': {}
        }

def save_tracking_data(output_dir, tracking_data):
    """
    Sauvegarde les données de suivi dans tracking.pkl.
    """
    tracking_file = os.path.join(output_dir, "tracking.pkl")
    
    with open(tracking_file, "wb") as f:
        pickle.dump(tracking_data, f)
    
    print(f"Données de suivi sauvegardées dans {tracking_file}")

def get_next_import_number(output_dir):
    """
    Retourne le prochain numéro d'importation à utiliser.
    """
    tracking_data = load_tracking_data(output_dir)
    return tracking_data['import_count'] + 1

def save_log(output_dir, import_number, log_entries):
    """
    Crée un fichier de log détaillé pour cette importation avec:
    - Nouvelles cartes importées
    - Cartes modifiées (avec ancien et nouveau contenu)
    - Cartes non modifiées
    """
    output_dir = output_dir+"\logs"
    os.makedirs(output_dir, exist_ok=True)

    log_file = os.path.join(output_dir, f"log-{import_number}.txt")
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"=== LOG D'IMPORTATION #{import_number} ===\n")
        f.write(f"Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        
        # Nouvelles cartes
        new_cards = [e for e in log_entries if e['status'] == 'new']
        if new_cards:
            f.write(f"NOUVELLES CARTES IMPORTÉES ({len(new_cards)}):\n")
            f.write("-"*60 + "\n")
            for entry in new_cards:
                f.write(f"\n[{entry['type']}] Carte n°{entry['number']}: {entry['title']}\n")
                f.write(f"Contenu: {entry['content']}\n")
            f.write("\n")
        
        # Cartes modifiées
        modified_cards = [e for e in log_entries if e['status'] == 'modified']
        if modified_cards:
            f.write(f"CARTES MODIFIÉES ({len(modified_cards)}):\n")
            f.write("-"*60 + "\n")
            for entry in modified_cards:
                f.write(f"\n[{entry['type']}] Carte n°{entry['number']}: {entry['title']}\n")
                f.write(f"\n>>> ANCIEN CONTENU:\n{entry['old_content']}\n")
                f.write(f"\n>>> NOUVEAU CONTENU:\n{entry['content']}\n")
            f.write("\n")
        
        # Cartes non modifiées
        unchanged_cards = [e for e in log_entries if e['status'] == 'unchanged']
        if unchanged_cards:
            f.write(f"CARTES NON MODIFIÉES ({len(unchanged_cards)}):\n")
            f.write("-"*60 + "\n")
            for entry in unchanged_cards:
                f.write(f"[{entry['type']}] Carte n°{entry['number']}: {entry['title']}\n")
            f.write("\n")
        
        # Résumé
        f.write("="*60 + "\n")
        f.write(f"RÉSUMÉ:\n")
        f.write(f"  Nouvelles cartes: {len(new_cards)}\n")
        f.write(f"  Cartes modifiées: {len(modified_cards)}\n")
        f.write(f"  Cartes inchangées: {len(unchanged_cards)}\n")
        f.write(f"  Total traité: {len(log_entries)}\n")
    
    print(f"Log sauvegardé dans {log_file}")

def file_header(output_dir, import_number):
    """
    Crée le fichier cartes-X.txt avec l'en-tête nécessaire pour Anki.
    """
    filename = os.path.join(output_dir, f"cartes-{import_number}.txt")
    with open(filename, "w", encoding="utf-8") as out:
        # en tête du fichier, pour donner le nom du paquet et le type de carte
        out.write("#separator:;\n")
        out.write("#columns:paquet;Front;type;Back;démo\n")
        out.write("#notetype:maths\n")
        out.write("#deck column:1\n")
    return filename

def extract_latex_by_subsection(tex, output_dir, envs, chemin, num_chapitre, ofset=1):
    """
    Extrait les environnements LaTeX (théorèmes, propriétés, etc.) par sous-section,
    en tenant compte de la section parente, même si plusieurs sections existent.
    
    Système de tracking basé sur le numéro de carte:
    - Ne traite que les cartes au-delà du dernier numéro importé
    - Détecte les modifications de contenu pour les cartes existantes
    - Crée un nouveau fichier cartes-X.txt seulement s'il y a de nouvelles cartes
    - Génère un log-X.txt détaillé pour chaque importation
    """
    # Charge les données de suivi
    tracking_data = load_tracking_data(output_dir)
    last_imported = tracking_data['last_card_number']
    card_versions = tracking_data['card_versions']
    import_number = get_next_import_number(output_dir)
    
    # compteur pour les numéros des propriétés, théorèmes, etc.
    counter = 1

    # compteur pour les parties
    section_count = 0
    # compteur pour les sous-sections
    subsection_count = 0

    # associe à chaque titre de propriété le nombre de fois qu'elle apparait pour ajouter ce numéro en cas de doublons
    seen_titles = {}

    # Liste pour le log détaillé
    log_entries = []
    
    # Liste des nouvelles cartes à écrire dans le fichier cartes-X.txt
    new_cards_to_write = []
    
    # Statistiques
    stats = {
        'new': 0,
        'modified': 0,
        'unchanged': 0,
        'skipped_by_offset': 0
    }

    # Regex pour trouver toutes les sections et sous-sections dans l'ordre
    block_pattern = re.compile(
        r'(\\section\{([^\}]*)\}|\\subsection\{([^\}]*)\})',
        re.DOTALL
    )
    env_pattern = re.compile(
    r'\\begin\{(' + '|'.join(envs) + r')\}(?:\{([^\}]*)\}\{[^\}]*\})?(.*?)\\end\{\1\}',
    re.DOTALL
    )

    os.makedirs(output_dir, exist_ok=True)

    # Trouve tous les blocs (sections et sous-sections) dans l'ordre
    blocks = list(block_pattern.finditer(tex))
    current_section = None

    for i, block in enumerate(blocks):
        block_type = 'section' if block.group(2) is not None else 'subsection'
        block_name = block.group(2) if block_type == 'section' else block.group(3)

        if block_type == 'section':
            current_section = block_name.strip()
            section_count += 1
            subsection_count = -1  # Réinitialise le compteur de sous-sections à -1 car on fait +1 juste après, alors qu'on est pas encore dans une sous-section
            subsection_name = None  # Réinitialise le nom de la sous-section

        elif block_type == 'subsection' and current_section is not None:
            subsection_name = block_name.strip()

        # Le contenu de la sous-section va jusqu'au prochain bloc (section ou sous-section) ou fin du document
        start = block.end()
        end = blocks[i+1].start() if i+1 < len(blocks) else len(tex)
        content = tex[start:end]
        results = []
        # Incrémente le compteur de sous-sections
        subsection_count += 1

        for match in env_pattern.finditer(content):
            env_type = match.group(1)

            # recto de la carte 
            title = match.group(2)

            if title == "":
                title = None

            #Cas où le titre a été oublié
            if title == None :
                title = "Titre oublié"
                print(f"/!\\ titre oublié pour {env_type}.{counter} dans la section '{current_section}', sous-section '{subsection_name}'")
            else : 
                title = title.strip()

            # Si c'est une définition, on ajoute le mot "Définition" au titre
            if env_type == "definition":
                debut = title[0:3]
                debut.capitalize()

                if debut != "Def":
                    if len(title) > 0:
                        title = f"Def {title[0].lower()}{title[1:]}"
                    else : 
                        title = "Def"
                else :
                    title = title[0].capitalize() + title[1:]
                    pass
            
                env_type = "Définition"

            elif env_type == "propriete":
                env_type = "Propriété"

            elif env_type == "theoreme":
                env_type = "Théorème"
            

            # gère les doublons de titre pour éviter les problèmes dans anki
            # Si le titre a déjà été vu, on le print et on incrémente le compteur pour éviter les doublons
            if title in seen_titles:
                print(f"Attention, doublon pour '{title}' dans la section '{current_section}', sous section '{subsection_name}'") 

                # Si le titre a déjà été vu, on incrémente le compteur pour éviter les doublons
                seen_titles[title] += 1

                # modification du titre de la carte pour signaler le doublon 
                title += f" /!\\ doublon, n°{seen_titles[title]}"

                print(f"Le titre devient '{title}'")
                print()
            else : 
                # Si le titre n'a pas été vu, on l'ajoute au dictionnaire
                seen_titles[title] = 1

                
            env_content = re.sub(r'\s+', ' ', match.group(3).strip())
            # formate le type de carte et ajoute le numéro du chapitre et le compteur
            type_num = f"{env_type} {num_chapitre}.{counter}"

            # Construction du chemin de la carte
            chemin_actuel = chemin
            if subsection_name is None:
                chemin_actuel = f"{chemin}::{num_chapitre}.{section_count} {current_section}"
            else:
                chemin_actuel = f"{chemin}::{num_chapitre}.{section_count} {current_section}::{num_chapitre}.{section_count}.{subsection_count} {subsection_name}"

            # Détermine le statut de la carte
            status = None
            old_content = None
            
            if counter <= last_imported:
                # Carte déjà importée précédemment
                if counter in card_versions:
                    old_title = card_versions[counter]['title']
                    old_content = card_versions[counter]['content']
                    
                    if old_title == title and old_content == env_content:
                        # Aucun changement
                        status = 'unchanged'
                        stats['unchanged'] += 1
                        print(f"Carte n°{counter} '{title}' inchangée")
                    else:
                        # Carte modifiée
                        status = 'modified'
                        stats['modified'] += 1
                        print(f"/!\\ Carte n°{counter} modifiée: '{title}'")
                        print(f"    Ancien: titre='{old_title}'")
                        print(f"    Nouveau: titre='{title}'")
                        
                        # On met à jour la version
                        card_versions[counter] = {'title': title, 'content': env_content}
                else:
                    # Carte dans la plage importée mais pas dans l'historique (cas rare)
                    status = 'modified'
                    stats['modified'] += 1
                    card_versions[counter] = {'title': title, 'content': env_content}
            else:
                # Nouvelle carte (au-delà du dernier numéro importé)
                status = 'new'
                stats['new'] += 1
                print(f"Nouvelle carte n°{counter} '{title}' ajoutée")
                
                # Enregistre la version
                card_versions[counter] = {'title': title, 'content': env_content}
                
                # Ajoute à la liste des cartes à écrire (seulement si >= offset)
                if counter >= ofset:
                    card_line = f"{sanitize_title(chemin_actuel)};{sanitize_content(title[0].capitalize() + title[1:])};{sanitize_content(type_num[0].capitalize() + type_num[1:])};{sanitize_content(env_content[0].capitalize() + env_content[1:])}"
                    new_cards_to_write.append(card_line)
                else:
                    stats['skipped_by_offset'] += 1

            # Crée l'entrée de log
            log_entry = {
                'number': counter,
                'title': sanitize_title(title),
                'type': type_num,
                'content': sanitize_content(env_content),
                'status': status,
                'section': chemin_actuel
            }
            
            if status == 'modified' and old_content:
                log_entry['old_content'] = sanitize_content(old_content)
            
            log_entries.append(log_entry)

            # Incrémente le numéro pour la prochaine propriété, théorème, etc.
            counter += 1

    # Mise à jour du dernier numéro de carte traité
    last_card_processed = counter - 1
    
    print()
    print("="*60)
    print(f"Extraction terminée. {last_card_processed} cartes traitées.")
    print(f"Nouvelles cartes: {stats['new']}")
    print(f"Cartes modifiées: {stats['modified']}")
    print(f"Cartes inchangées: {stats['unchanged']}")
    if stats['skipped_by_offset'] > 0:
        print(f"Cartes ignorées (offset): {stats['skipped_by_offset']}")
    print("="*60)
    
    # Sauvegarde des données de suivi
    tracking_data['last_card_number'] = last_card_processed
    tracking_data['card_versions'] = card_versions
    
    # Si de nouvelles cartes à importer, crée le fichier cartes-X.txt
    if new_cards_to_write:
        tracking_data['import_count'] = import_number
        cards_file = file_header(output_dir, import_number)
        
        with open(cards_file, "a", encoding="utf-8") as out:
            for line in new_cards_to_write:
                out.write(line + "\n")
        
        print(f"\n✓ Fichier {os.path.basename(cards_file)} créé avec {len(new_cards_to_write)} nouvelles cartes")
    else:
        print(f"\nℹ Aucune nouvelle carte à importer, pas de fichier cartes-{import_number}.txt créé")
    
    # Sauvegarde du tracking
    save_tracking_data(output_dir, tracking_data)
    
    # Génère le log détaillé
    save_log(output_dir, import_number, log_entries)

def open_file(filename):
    """Ouvre un fichier et retourne son contenu."""
    with open(filename, encoding="utf-8") as f:
        return f.read()
    
def extraction_chapitre(file_name: str):
    file = None
    if os.path.exists(file_name):
        file = open_file(file_name)
    else : 
        print("le fichier latex de sortie n'a pas pu être créé, problème à l'ouverture expansion des raccourcis")
        return

    # Recherche le numéro et le titre du chapitre dans le fichier LaTeX
    pattern = r"\\chapitre\{([^\}]+)\}\{([^\}]+)\}"
    match = re.search(pattern, file)

    if match:
        numero = match.group(1)
        titre = match.group(2)
        print(f"Numéro du chapitre : {numero}")
        print(f"Titre du chapitre : {titre}")
        return(numero, titre)
    else:
        print("Aucun chapitre trouvé.")
        return (-1, "titre inconnu")

def test_mode():
    file = open_file("test.tex")
    (numero_chapitre, nom_chapitre) = (0, "test")
    paquet = "prépa::MP2I::maths::Chapitre 0, test"
    print(f"nom du paquet : '{paquet}'")
    envs = ["theoreme", "propriete", "corollaire", "definition", "proposition", "lemme"]
    extract_latex_by_subsection(file, "test_output", envs, paquet, numero_chapitre)

def normal_mode(numero_chapitre, working_path, ofset=1):
    """
    Fonction principale pour l'extraction des cartes LaTeX.
    """

    envs = ["theoreme", "propriete", "corollaire", "definition", "proposition", "lemme", 
            "theorement", "proprietent", "corollairent", "definitionnt", "propositionnt", "lemment"]

    #le nom du paquet dans lequel le paquet contenant le chapitre entier doit être placé
    paquet = "prépa::MPI::maths::cours::"
    
    tex_path = rf"{working_path}\chapitre{numero_chapitre}"
    header_file_path = rf"{tex_path}\chapitre{numero_chapitre}.tex"
    tex_file_path = rf"{tex_path}\cours\contenu.tex"
    sty_file_path = rf"{working_path}\commun\raccourcis.sty"
    
    # Option 1: Utiliser le script expand.bat pour l'expansion des raccourcis
    print("Expansion des raccourcis LaTeX...")
    expanded_file = f"chapitre{numero_chapitre}_expanded.tex"
    expanded_file = rf"{working_path}\scripts_anki\latex\{expanded_file}"

    # gère le remplacement des raccourcis du fichier Latex
    expand_shortcuts_complete.main(tex_file_path, sty_file_path, expanded_file)
    
    file = None
    if os.path.exists(expanded_file):
        file = open_file(expanded_file)
    else : 
        print("le fichier latex de sortie n'a pas pu être créé, problème à l'ouverture expansion des raccourcis")
        return

    # Récupère le numéro et nom du chapitre depuis le latex
    (numero_chapitre, nom_chapitre) = extraction_chapitre(header_file_path)

    # Construit le chemin du paquet pour l'entête deck
    paquet = paquet + "[" + str(numero_chapitre).zfill(2) + "] - " + nom_chapitre
    print(f"nom du paquet : '{paquet}'")

    print()
    # Lance l'extraction et la création des fichiers par sous-section
    paquet_paths = rf"{working_path}\scripts_anki\paquets\paquets_chapitre{numero_chapitre}"
    extract_latex_by_subsection(file, paquet_paths, envs, paquet, numero_chapitre, ofset)

def autre_fichier(file_path, filename, paquet, output_file):
    """
    Extraie le contenu du fichier passé en argument, 
    pas besoin de la structure habiu=tuel de chapitre, ne prend en compte que le fichier tex donné
    Pas d'expension des raccourcis non plus
    Nom paquet : nom du paquet anki créé
    """

    envs = ["theoreme", "propriete", "corollaire", "definition", "proposition", "lemme", 
            "theorement", "proprietent", "corollairent", "definitionnt", "propositionnt", "lemment"]
    
    tex_file_path = rf"{file_path}\{filename}"

    file = None
    if os.path.exists(tex_file_path):
        file = open_file(tex_file_path)
    else : 
        print("le fichier latex de sortie n'a pas pu être créé, problème à l'ouverture expansion des raccourcis")
        return

    print(f"nom du paquet : '{paquet}'")

    print()
    # Lance l'extraction et la création des fichiers par sous-section
    paquet_paths = rf"C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\maths\cours\scripts_anki\paquets\{output_file}"
    extract_latex_by_subsection(file, paquet_paths, envs, paquet, 1, 0)


def main():
    """
    Fonction principale pour l'extraction des cartes LaTeX.
    
    Arguments de ligne de commande :
        --chapitre, -c : Numéro du chapitre à traiter (obligatoire)
        --offset, -o : Numéro de la propriété/théorème à partir duquel commencer (défaut: 1)
        --test, -t : Active le mode test (utilise test.tex)
    
    Exemples :
        python importation_auto.py -c 11
        python importation_auto.py --chapitre 11 --offset 25
        python importation_auto.py -c 5 -o 10
    """
    parser = argparse.ArgumentParser(
        description='Extraction automatique de cartes Anki depuis un cours LaTeX',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python importation_auto.py -c 11
  python importation_auto.py --chapitre 11 --offset 25
  python importation_auto.py -c 5 -o 10 --test
        """
    )
    
    parser.add_argument(
        '-c', '--chapitre',
        type=int,
        required=True,
        help='Numéro du chapitre à traiter'
    )
    
    parser.add_argument(
        '-o', '--offset',
        type=int,
        default=0,
        help='Numéro de la propriété/théorème à partir duquel commencer (défaut: 0)'
    )
    
    parser.add_argument(
        '-t', '--test',
        action='store_true',
        help='Active le mode test (utilise test.tex au lieu du chapitre)'
    )
    
    args = parser.parse_args()
    
    # Répertoire dans lequel tout se trouve
    base_path = rf"C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\maths\cours"

    if args.test:
        print("Mode test activé")
        test_mode()
    else:
        print(f"Traitement du chapitre {args.chapitre} avec offset {args.offset}")
        normal_mode(args.chapitre, base_path, args.offset)



if __name__ == "__main__":
    if True : 
        main()
    else : 
        autre_fichier(rf"C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\maths\cours\memento_X_ens", 
                      "theorie_ensemble_algebre_lineaire.tex", 
                      "prépa::MPI::maths::cours::[00] - suppléments::[52] - Memento X-ens::[01] - Ensembles et algèbre linéaire",
                      "memento_X_ens_ensembles_algebre_lineaire")
        # normal_mode(15, rf"C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\maths\cours", 0)