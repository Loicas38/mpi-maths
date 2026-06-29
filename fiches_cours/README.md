# Extracteur de cartes Anki vers LaTeX

Ce script extrait automatiquement vos cartes Anki et les convertit en documents LaTeX structurés par chapitres, avec support des titres de cartes et champs additionnels.

## Prérequis

### 1. AnkiConnect
Installez le greffon AnkiConnect dans Anki :
1. Ouvrez Anki
2. Allez dans **Outils** > **Modules complémentaires** > **Parcourir et installer**
3. Collez le code : `2055492159`
4. Redémarrez Anki

### 2. Python
- Avoir python installé, n'importe quelle version devrait faire l'affaire

### 3. LaTeX
Pour compiler les PDFs, installez une distribution LaTeX :
- **Windows** : MiKTeX (https://miktex.org/) ou TeX Live
- **Linux** : `sudo apt-get install texlive-full`
- **macOS** : MacTeX (https://www.tug.org/mactex/)
- **En ligne** : sur overleaf par exemple

## Configuration

Toute la configuration se fait au début du fichier `anki_to_latex.py` :

### Choix du paquet à extraire
```python
# Paquet principal à extraire
main_deck = "prépa::MPI::maths::cours"

# Si True, traite chaque sous-paquet direct dans un fichier séparé
apply_to_all_subdecks = True
```

### Configuration des types de cartes
Définissez pour chaque type de carte Anki (modelName) :
- **title_field** : Champ utilisé comme titre de la carte (obligatoire il me semble)
- **content_field** : Champ principal de la carte
- **extra_fields** : Liste de champs à afficher en dessous du cadre
- **sort_field** : Champ de tri (optionnel)
- **check_roman_numbering** : Si `True` et après échec à trier selon le champ spécifié en convertissant en int, cherche un chiffre romain en prenant toutes les majuscules du champ. 

```python
card_types_config = {
    "maths": {
        "title_field": "Front",      # Le Front devient le titre
        "content_field": "Back",     # Le Back est le contenu
        "extra_fields": ["démo"]     # La démo s'affiche en dessous
    },
    "Simple [Bôtiful]": {
        "title_field": "Recto",         
        "content_field": "Verso",
        "extra_fields": []
    },
    "citations" :{
            "title_field": "Recto",
            "content_field": "Verso",
            "extra_fields": ["chapitre", "page"],
            "sort_field": "page",
            "check_roman_numbering": True 
    }
}
```

### Compilation 

Activer ou non la compilation automatique après extraction à la fin du script. Attention, certains caractères spéciaux ou les émojis ne peuvent pas être compilés par latex.

## Utilisation

1. **Assurez-vous qu'Anki est ouvert** avec AnkiConnect actif

2. **Configurez le script** (voir section Configuration)

3. **Lancez le script** :
   ```bash
   python anki_to_latex.py
   ```
   Ou double-cliquez sur `run.bat` (Windows)

4. Le script va :
   - Se connecter à Anki
   - Extraire les cartes selon votre configuration
   - Détecter les modifications depuis la dernière exécution
   - Générer les fichiers LaTeX par paquet
   - Compiler automatiquement les PDFs

## Structure des fichiers générés

```
output/
├── ankicards.cls                           # Classe LaTeX commune
├── prépa_MPI_maths_cours_[01] - Algèbre/  # Un dossier par sous-paquet
│   ├── images/                             # Images extraites d'Anki
│   │   ├── image1.png
│   │   └── image2.jpg
│   ├── prépa_MPI_maths_cours_[01] - Algèbre.tex
│   └── prépa_MPI_maths_cours_[01] - Algèbre.pdf
├── prépa_MPI_maths_cours_[02] - Analyse/
│   ├── images/
│   ├── prépa_MPI_maths_cours_[02] - Analyse.tex
│   └── prépa_MPI_maths_cours_[02] - Analyse.pdf
└── ...
```

## Fonctionnalités

### Types de cartes LaTeX générées

Le script génère automatiquement 3 types de cartes selon la configuration :

**1. Carte simple** (sans titre) :
```
┌─────────────────────────┐
│  Contenu de la carte    │
└─────────────────────────┘
```

**2. Carte avec titre** :
```
┌─────────────────────────┐
│ ┌───────────────────┐   │
│ │ Titre (fond bleu) │   │
│ └───────────────────┘   │
│                         │
│  Contenu de la carte    │
└─────────────────────────┘
```

**3. Carte avec titre et champs extra** :
```
┌─────────────────────────┐
│ ┌───────────────────┐   │
│ │ Titre (fond bleu) │   │
│ └───────────────────┘   │
│                         │
│  Contenu de la carte    │
└─────────────────────────┘
  Champs additionnels...
```

### Détection des modifications
Le script garde en cache l'état de vos cartes et vous alerte si :
- De nouvelles cartes ont été ajoutées ✓
- Des cartes ont été modifiées ✓
- Des cartes ont été supprimées ✓

### Conversion HTML/MathJax → LaTeX
Le script convertit automatiquement :
- **Texte formaté** : gras, italique, souligné
- **Listes** : numérotées et à puces (même dans les titres)
- **Mathématiques** : MathJax → LaTeX natif
- **Environnements math** : `align`, `equation`, etc. (sans imbrication incorrecte)
- **Structure HTML** : div, br, span, etc.
- **Images** : téléchargées depuis Anki et intégrées avec `\includegraphics`

### Hiérarchie des sections
Les paquets et sous-paquets Anki sont convertis en sections LaTeX :
- Niveau 1 → `\section{}`
- Niveau 2 → `\subsection{}`
- Niveau 3+ → `\subsubsection{}`

### Évite les doublons
Chaque carte n'apparaît qu'une seule fois, dans le paquet où elle est réellement stockée (pas dans les paquets parents).

## Personnalisation avancée

### Modifier le style des cartes
Éditez le fichier généré `output/ankicards.cls` pour personnaliser :
- Couleurs du cadre et du titre
- Marges et espacements
- Police et taille
- Style du rectangle de titre

### Ajouter un nouveau type de carte
Dans `card_types_config`, ajoutez une nouvelle entrée :
```python
"Mon Type de Carte": {
    "title_field": "Question",
    "content_field": "Réponse",
    "extra_fields": ["Source", "Notes"]
}
```

## Dépannage

### "Impossible de se connecter à Anki"
- Vérifiez qu'Anki est ouvert
- Vérifiez qu'AnkiConnect est installé et activé
- Vérifiez qu'aucun pare-feu ne bloque le port 8765

### "Type de carte 'XXX' non configuré"
- Ajoutez ce type de carte dans `card_types_config`
- Ou ignorez-le (les cartes seront simplement sautées)

### "pdflatex n'est pas installé"
- Installez une distribution LaTeX (voir Prérequis)
- Vérifiez que `pdflatex` est dans votre PATH

### Erreurs LaTeX lors de la compilation
- Vérifiez le fichier `.log` correspondant dans le dossier output
- Les packages requis : `tcolorbox`, `amsmath`, `babel[french]`

### Caractères spéciaux mal affichés
- Assurez-vous que votre distribution LaTeX supporte l'UTF-8
- Le script utilise `\RequirePackage[utf8]{inputenc}`

### Images manquantes ou mal affichées
- Vérifiez que les images existent dans votre collection Anki
- Les images sont automatiquement téléchargées via AnkiConnect
- Les images sont sauvegardées dans le dossier `images/` de chaque document
- Les dimensions sont converties automatiquement (px → cm)
- Par défaut, une image sans dimensions utilise 80% de la largeur de la page

## Cache et données

**`anki_cache.json`** : Stocke l'état des cartes pour détecter les modifications.
- Supprimez-le pour réinitialiser la détection de changements
- Il se met à jour automatiquement à chaque exécution

## Exemples d'utilisation

### Extraire un seul paquet
```python
main_deck = "prépa::MPI::maths::cours"
apply_to_all_subdecks = False
```

### Extraire tous les sous-paquets séparément
```python
main_deck = "prépa::MPI::maths::cours"
apply_to_all_subdecks = True
```

### Carte sans titre ni champs extra
```python
"Simple": {
    "title_field": None,
    "content_field": "Back",
    "extra_fields": []
}
```

### Carte avec plusieurs champs additionnels
```python
"Complexe": {
    "title_field": "Question",
    "content_field": "Réponse",
    "extra_fields": ["Démonstration", "Remarques", "Source"]
}
```
