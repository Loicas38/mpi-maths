"""
Ce fichier crée un fichier .txt à partir d'un fichier tex pour anki. 
Il suffit d'importer le fichier générer dans anki et les paquets sont générées, les type de carte
gérés, les cartes remplies, .... 

De plus les abréviations présentes dans le fichier LaTeX sont remplacées par leur équivalent.
"""


import re
import os
import pickle
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

def search_history(output_dir):
    """
    Cherche un fichier d'historique dans le répertoire de sortie.
    Si le fichier existe, charge l'historique des cartes déjà traitées.
    """
    history_file = os.path.join(output_dir, "history.pkl")
    
    if os.path.exists(history_file):
        with open(history_file, "rb") as f:
            return pickle.load(f)
    else:
        return {}
    
def save_history(output_dir, history):
    """
    Sauvegarde l'historique des cartes traitées dans un fichier.
    """
    history_file = os.path.join(output_dir, "history.pkl")
    
    with open(history_file, "wb") as f:
        pickle.dump(history, f)
    
    print(f"Historique sauvegardé dans {history_file}")

def save_log(output_dir, modified, created, not_modified):
    """
    crée des fichiers de log pour les cartes traitées, les cartes modifiées et les cartes non modifiées.
    """
    # Crée le dossier logs s'il n'existe pas
    logs_dir = os.path.join(output_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    with open(os.path.join(logs_dir, "log_modified.txt"), "w", encoding="utf-8") as f:
        for card in modified:
            f.write(f"{card}\n\n")  
        f.write(f"Nombre de cartes modifiées : {len(modified)}\n")  

    with open(os.path.join(logs_dir, "log_created.txt"), "w", encoding="utf-8") as f:
        for card in created:
            f.write(f"{card}\n\n")
        f.write(f"Nombre de cartes créées : {len(created)}\n")

    with open(os.path.join(logs_dir, "log_not_modified.txt"), "w", encoding="utf-8") as f:
        for card in not_modified:
            f.write(f"{card}\n\n")
        f.write(f"Nombre de cartes non modifiées : {len(not_modified)}\n")

def file_header(output_dir):
    """
    Crée le fichier cartes.txt avec l'en-tête nécessaire pour Anki.
    """
    with open(os.path.join(output_dir, "cartes.txt"), "w", encoding="utf-8") as out:
        # en tête du fichier, pour donner le nom du paquet et le type de carte
        out.write("#separator:;\n")
        out.write("#columns:paquet;Front;type;Back;démo\n")
        out.write("#notetype:maths\n")
        out.write("#deck column:1\n")

def extract_latex_by_subsection(tex, output_dir, envs, chemin, num_chapitre, ofset=1):
    """
    Extrait les environnements LaTeX (théorèmes, propriétés, etc.) par sous-section,
    en tenant compte de la section parente, même si plusieurs sections existent.
    """
    # compteur pour les numéros des propriétés, théorèmes, etc.
    counter = 1

    # compteur pour les parties
    section_count = 0
    # compteur pour les sous-sections
    subsection_count = 0

    # associe à chaque titre de propriété le nombre de fois qu'elle apparait pour ajouter ce numéro en cas de doublons
    seen_titles = {}

    # Compteurs pour les cartes traitées
    # uniquement à des fins de stats et d'affichage, pas d'utilité pour le programme 
    counter_ignore = 0
    counter_added = 0
    counter_modified = 0

    # liste contenant les logs
    modified_cards = []
    created_cards = []
    not_modified_cards = []

    # enregistre les propriétés, def, ... qui ont étées vues, et en quelle position, enregistre cela dans un dico
    # puis dans un fichier. Le fichier sera utilisé, lorsqu'il existe, pour savoir où reprendre, et vérifier 
    # que les éléments déjà importés n'ont pas éété modifiés depuis la dernière importation.
    # les clés du dico sont les identitifants, et les valeurs des tuples (titre, contenu)
    history = search_history(output_dir)


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

    # Crée le fichier cartes.txt avec l'en-tête nécessaire pour Anki
    file_header(output_dir)


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
                    title = f"Def {title}"
                else :
                    title = title.capitalize()
            
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
            type_num = f"{env_type.capitalize()} {num_chapitre}.{counter}"

            # on regarde si on a déjà des données pour cet indice de propriété, théorème, etc.
            if counter in history:
                # Si on a déjà une carte pour cet indice, on vérifie si le titre et le contenu sont les mêmes
                # Si oui, on ne fait rien, sinon on remplace l'ancienne carte par la nouvelle
                if history[counter][0] == title and history[counter][1] == env_content:
                    print(f"Carte '{title}' ignorée car déjà importée dans la section '{current_section}', sous-section '{subsection_name}'")
                    print()
                    counter += 1
                    counter_ignore += 1
                    not_modified_cards.append(f"carte dans : {chemin}::{num_chapitre}.{section_count} {current_section}::{num_chapitre}.{section_count}.{subsection_count} {subsection_name}, \n titre = {sanitize_title(title)} \n type = {sanitize_content(type_num)} \n contenu = {sanitize_content(env_content)}")
                    # on continue pour ne pas ajouter la carte dans le fichier
                    continue
                else : 
                    print("/!\\ conflit entre ancienne et nouvelle carte : ")
                    print(f"dans la section '{current_section}', sous-section '{subsection_name}', contenu n° {counter}")
                    print(f"Ancienne carte : recto = '{history[counter][0]}', contenu = '{history[counter][1]}'")
                    print(f"Remplacée par : recto = '{title}', verso = '{env_content}' ")
                    print()
                    counter_modified += 1
                    history[counter] = (title, env_content)
                    modified_cards.append(f"carte dans : {chemin}::{num_chapitre}.{section_count} {current_section}::{num_chapitre}.{section_count}.{subsection_count} {subsection_name}, \n titre = {sanitize_title(title)} \n type = {sanitize_content(type_num)} \n contenu = {sanitize_content(env_content)}")
            else:
                # Enregistre la nouvelle carte dans l'historique
                print(f"Nouvelle carte '{title}' ajoutée dans la section '{current_section}', sous-section '{subsection_name}'")
                print()
                counter_added += 1
                history[counter] = (title, env_content)
                created_cards.append(f"carte dans : {chemin}::{num_chapitre}.{section_count} {current_section}::{num_chapitre}.{section_count}.{subsection_count} {subsection_name}, \n titre = {sanitize_title(title)} \n type = {sanitize_content(type_num)} \n contenu = {sanitize_content(env_content)}")

            # n'ajoute la carte que si on est au delà de l'ofset
            if counter >= ofset:
                results.append(f'"{sanitize_content(title)}";"{sanitize_content(type_num)}";"{sanitize_content(env_content)}"')

            # Incrémente le numéro pour la prochaine propriété, théorème, etc.
            counter += 1

        if results:
            chemin_actuel = chemin
            # on ajoute les éléments nécessaires en fonction de s'il y a une sous section ou non 
            if subsection_name is None:
                # Si pas de sous-section, on utilise juste le nom de la section
                chemin_actuel = f"{chemin}::{num_chapitre}.{section_count} {current_section}"
                
            else:
                # Si sous-section, on ajoute le nom de la sous-section
                chemin_actuel = f"{chemin}::{num_chapitre}.{section_count} {current_section}::{num_chapitre}.{section_count}.{subsection_count} {subsection_name}"


            with open(os.path.join(output_dir, "cartes.txt"), "a", encoding="utf-8") as out:
                for line in results:
                    out.write(sanitize_title(f"{chemin_actuel}") + ";" + line + "\n")

    # Enregistre l'historique des cartes traitées
    print(f"Extraction terminée. {counter-1} cartes traitées.")
    print(f"Cartes ignorées : {counter_ignore}, Cartes ajoutées : {counter_added}, Cartes modifiées : {counter_modified}")
    save_history(output_dir, history)

    save_log(output_dir, modified_cards, created_cards, not_modified_cards)
    print(f"Logs sauvegardés dans {output_dir}/logs")

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
    tex_file_path = rf"{tex_path}\contenu.tex"
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



def main():
    """
    Fonction principale pour l'extraction des cartes LaTeX.
    """
    test = False  # Changez à True pour le mode test (utilisera le fichier test.tex de ce répertoire)
    numero_chapitre = 11  # chapitre à traiter
    ofset = 25
    # numéro de la proprété, théorème, ... à partir duquel on commence (utile si on veut reprendre un import interrompu)
    # répertoir dans lequel tout se trouve
    base_path = rf"C:\Users\lucas\OneDrive\Documents\cours\prépa\MPI\maths\cours"

    if test:
        test_mode()
    else:
        normal_mode(numero_chapitre, base_path, ofset)



if __name__ == "__main__":
    main()