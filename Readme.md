# Fonctionnement de la classe Latex prepacours.cls

## installation et compilation 

J'utilise personnelement Miktex. Pour le faire fonctionner, il a d'abord fallu installer strawberry, puis miktex. Ensuite, vous pouvez l'utiliser en ligne de commande ou directement dans VS code avec l'extension latex workshop qui est vraiment bien. On peut aussi faire un script python qui gère la compilation.

On peut également compiler en ligne sur des sites comme overleaf. 

## Aide 

La page wipipedia aide au formules tex (https://fr.wikipedia.org/wiki/Aide:Formules_TeX) contient à peu près tout ce qui est nécessaire pour écrire du latex. 

Vous pouvez également activer copilot dans vs code avec les suggestions. Il est vraiment très puissant et devine assez souvent ce que vous vouliez écrire. 

## Environnements personalisés 

Il existe un certain nombre d'environnements personalisés à destination des 
propositions, théorèmes, ... 

Voici un exemple d'utilisation pour une proposition : 

```latex
\begin{proposition}{Titre de la proposition (facultatif)}{}
    Contenu de la proposition 
\end{proposition}
```

Il est nécessaire de mettre les accolades contenant le titre et les accolades vides, sinon le début du contenu de la proposition sera coupé. 

Il existe également une variante des environnements permettant de mettre un titre sans que celui-ci ne soit affiché : 

```latex
\begin{propositionnt}{Titre qui ne sera pas affiché}{}
    Contenu
\end{propositionnt}
```

Tous les environnements peuvent fonctionner dans ce mode en ajoutant simplement "nt" à la fin du mot. 


Il existe également les environnements "idée" pour mettre par exmple une idée du principe général des preuves. Ceux si cont affichés dans la marge au niveau de l'endroit où ils sont appelés. Ils s'utilisent comme suit : 

```latex
\idee{
    Idée de la preuve. 
}
```

Pour les preuves, l'environnement utilisé n'est pas de moi. Il se trouve dans un des package utilisés. 

```latex
\begin{proof}
    Contenu de la preuve. 
\end{proof}
```

Par défaut, le package affiche "Démonstration", puis le contenu fournit. Il est possible de modifier ce titre de cette façon : 

```latex
\begin{proof}[Titre]
    Contenu de la preuve. 
\end{proof}
```

"Titre" sera alors affiché à la place de "Démonstration". 

## Titres 

Il existe différents niveaux de titres, dans cet ordre : 

```latex
\section{grand titre}
\subsection{taille en dessous}
\subsubsection{Encore plus petit}
\paragraph{Plus vraiment un titre...}
```

Seuls les deux premiers sont affichés dans la table des matières. La profondeur de la table des matières peut être modifiée dans le fichier prépacours.cls, en augmentant ou diminuant le paramètre "tocdepth". 

## Commandes personalisées 

J'ai également un fichier de raccourcis pour gagner du temps lorsque je tape, réunis dans le fichier "raccourcis.sty". 

Pour les ensembles de nombres : 
```latex
\C, \R, \Q, \Z, \N
```
permettent d'obtenir le rendu des ensembles de nombres. 

Pourles fonctions : 
```latex
\fonction{nom de la fonction}{ensemble de départ}{ensemble d'arrivée}{variable}{formule}
```

Par exemple pour la fonction carré dans R : 
```latex
\fonction{f}{\R}{\R}{x}{x^2}
```

Lorsqu'il n'y a qu'un seul élément dans les accolades, celles ci peuvent être supprimées. Pour la fonction définie précédemment, on obtient : 
```latex
\fonction f \R \R x {x^2}
```

Les raccourcis suivants permettent eux de laisser un espace vertical "large", "average" (qui aurait plutôt du s'appeler medium) ou "small", en utilisant les commandes suivantes : 

```latex
\lvspace 
\avspace 
\svspace 
```

La hauteur de l'espace vertical créé peut être modifiée dans le fichier des raccourcis, et d'autres peuvent également être ajoutés. 

Un autre raccourci utile est \uindent. Celui-ci permet de créer un text qui va être souligné et indenté, avec un espace au dessus de celui-ci. Il est conseillé d'utiliser une commande pour laisser de l'espace vertical en dessous de celui-ci. 

J'ai créé de nombreux raccourcis pour tous les opérateurs classiques comme Vect, Ker, Sp, rg, cov, ... Vous pouvez retrouver la liste exhaustive dans le fichier raccourcis.sty. 


## Métadonnées

Avant de pouvoir compiler le fichier avec la clasee, il faut lui fournir un certain nombre de métadonnées, qui sont les suivantes : 

```latex
\annee{2025-2026}
\filiere{MPI / MPI*}
\etablissement{Lycée Champollion}
\auteur{Nom de l'auteur}
\chapitre{Numéro du chapitre (NECESSAIREMENT UN NOMBRE)}{titre du chapitre}
```

## Subtilitées 

N'étant pas un grand expert du latex, je n'ai pas trouvé de meilleur façon de faire ce qui suit (et ce n'est pas forcément super pratique)

Pour que la page de garde avec la table des matières apparaisse, ainsi que la première page de cours avec le titre en grand, il faut utiliser la commande \pagedegarde au tout début du contenu du document. Cela donne donc quelque chose du type : 

```latex
% métadonnées et importations

\begin{document}

\pagedegarde 

% contenu latex 

\end{document}
```


## Exercies et corrections 

Il y a également des environnements pour inclure des exos et leur correction. Pour cela, il existe des commandes permettant de passer du mode exos au mode cours, qui sont : 
```latex
\passerenmodeexos
\passerenmodecours
```

Les différents modes sont uniquement destinés à modifier la taille des en tête et des marges normalement. 

Il y a alors des environnement personalisés pour les exercies : 
```latex
\begin{exercice}
    Contenu de l'exo
\end{exercice}
```

et pour leur correction : 

```latex
\begin{correction}{nb}
    contenu correction
\end{correction}
```

Le champ "nb" permet de faire un lien vers l'exercice numéro "nb", pour ensuite permettre de passer de l'un à l'autre par un système de liens cliquables. 


## Template 

Normalement j'ai fourni un template qui contient l'arborescence que j'utilisais et que je trouve plutôt pratique pour ne pas avoir des fichiers de compilation partout, et qui permet d'avoir à la fois le cours, le TD, et un mix des deux. Au cas ou l'arborescence ce serait perdue, la voici : 

```
latex/
├── commun
|   ├── images
|   |   └── ampoule.png
|   ├── config.tex
|   ├── prepacours.cls
|   └── raccourcis.sty
├── chapitre1
|   ├── chapitre1.tex
|   ├── cours
|   |   ├── contenu.tex
|   |   └── cours1.tex
|   └── TD 
|       ├── contenu_td.tex
|       └── TD1.tex
|   
└── ...
```

Le fichier config.tex contient les métadonnées communes à tous les fichiers, prepacours.cls la classe personalisée, et réccourcis.sty les raccourcis. L'image ampoule.png est utilisée pour les environnements idee. 

Le fichier chapitre_.tex contient cela : 
```latex
\documentclass{../commun/prepacours}
\usepackage{../commun/raccourcis}

\input{../commun/config.tex}

\begin{document}
\chapitre{1}{Normes et distances}

\pagedegarde

\input{cours/contenu.tex}

\clearpage
\passerenmodeexos
\input{TD/contenu_td.tex}

\end{document}
```

Le fichier TD_.tex (qui utilise une autre classe fonctionnant globalement de la même façon) 
```latex
\documentclass{../../commun/prepacours_TD}
\usepackage{../../commun/raccourcis}

\input{../../commun/config.tex}
\chapitre{1}{TD : Normes et distances}

\begin{document}
\thispagestyle{premierepageschapitre}  % Pour avoir le style spécial en première page

\input{contenu_td.tex}

\end{document}

```

cours_.tex 
```latex
\documentclass{../../commun/prepacours}
\usepackage{../../commun/raccourcis}

\input{../../commun/config.tex}

\begin{document}
\chapitre{1}{Normes et distances}

\pagedegarde

\input{contenu.tex}

\end{document}
```

