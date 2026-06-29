# Support des images - Documentation technique

## Vue d'ensemble

Le script extrait automatiquement les images des cartes Anki et les intègre dans le document LaTeX généré.

## Fonctionnement

### 1. Détection des images
- Le script analyse le HTML de chaque carte pour détecter les balises `<img>`
- Les attributs `src`, `width`, et `height` sont extraits

### 2. Récupération via AnkiConnect
- L'image est téléchargée via l'API AnkiConnect (`retrieveMediaFile`)
- Les données sont retournées en base64
- Le fichier est décodé et sauvegardé localement

### 3. Organisation des fichiers
```
output/
└── prépa_MPI_maths_cours_[XX]/
    ├── images/              # Dossier créé automatiquement
    │   ├── image1.png
    │   ├── image2.jpg
    │   └── ...
    ├── document.tex
    └── document.pdf
```

### 4. Conversion LaTeX
Les balises HTML sont converties en commandes LaTeX :

**HTML:**
```html
<img src="image.png" width="500px" height="300px">
```

**LaTeX généré:**
```latex
\begin{center}
\includegraphics[width=13.23cm,height=7.94cm]{images/image.png}
\end{center}
```

## Gestion des dimensions

### Conversion pixels → centimètres
- Formule : `1px ≈ 0.0264583cm`
- Appliquée automatiquement aux attributs `width` et `height`

### Dimensions par défaut
- Si aucune dimension n'est spécifiée : `width=0.8\textwidth`
- L'image occupe 80% de la largeur de la page

### Préservation du ratio
- Si seule la largeur est spécifiée, la hauteur s'ajuste automatiquement
- Si seule la hauteur est spécifiée, la largeur s'ajuste automatiquement

## Exemples

### Image avec dimensions en pixels
**Anki (HTML):**
```html
<img src="diagram.png" width="400px">
```

**LaTeX généré:**
```latex
\begin{center}
\includegraphics[width=10.58cm]{images/diagram.png}
\end{center}
```

### Image sans dimensions
**Anki (HTML):**
```html
<img src="photo.jpg">
```

**LaTeX généré:**
```latex
\begin{center}
\includegraphics[width=0.8\textwidth]{images/photo.jpg}
\end{center}
```

### Image avec dimensions en unités LaTeX
**Anki (HTML):**
```html
<img src="logo.svg" width="5cm" height="3cm">
```

**LaTeX généré:**
```latex
\begin{center}
\includegraphics[width=5cm,height=3cm]{images/logo.svg}
\end{center}
```

## Gestion des erreurs

### Image introuvable
- Si l'image n'existe pas dans Anki, un message d'avertissement est affiché
- La balise `<img>` est simplement supprimée du document
- La compilation continue normalement

**Message:**
```
⚠ Erreur lors de la récupération de l'image 'missing.png': [détails]
```

### Image déjà téléchargée
- Chaque image n'est téléchargée qu'une seule fois par exécution
- Un cache en mémoire (`processed_images`) évite les doublons

## Formats supportés

Le script supporte tous les formats d'images compatibles avec LaTeX et le package `graphicx` :
- **PNG** (.png)
- **JPEG** (.jpg, .jpeg)
- **PDF** (.pdf) - vectoriel
- **EPS** (.eps) - vectoriel (avec conversion)
- **SVG** (.svg) - nécessite conversion ou package `svg`

⚠️ **Note:** Pour les SVG, assurez-vous d'avoir le package LaTeX `svg` ou convertissez-les en PDF.

## Centralisation dans le document

Les images sont centrées horizontalement grâce à l'environnement `center` :
```latex
\begin{center}
  \includegraphics[...]{...}
\end{center}
```

## Optimisation

### Éviter les téléchargements multiples
- Le cache `processed_images` suit les images déjà récupérées
- Utile quand la même image apparaît sur plusieurs cartes

### Chemins relatifs
- Les chemins dans le LaTeX sont relatifs : `images/filename.png`
- Facilite le déplacement du dossier de sortie

## Code technique

### Fonction principale : `_convert_images()`
Location: [anki_to_latex.py](anki_to_latex.py#L183)

**Responsabilités:**
1. Rechercher toutes les balises `<img>` avec regex
2. Extraire les attributs (src, width, height)
3. Télécharger l'image via AnkiConnect
4. Sauvegarder dans le dossier `images/`
5. Générer la commande `\includegraphics` correspondante

### Intégration dans le flux de conversion
- **Étape 5** du processus de conversion HTML → LaTeX
- Exécutée après l'extraction des environnements mathématiques
- Avant la conversion des listes et du texte formaté
